from __future__ import annotations

import atexit
import json
import logging
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import uuid
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

import markdown
import tomlkit
from flask import Flask, jsonify, render_template, request
from waitress import serve
from werkzeug.utils import secure_filename


APP_NAME = "TOOD Studio"
APP_VERSION = "1.1.0"
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def find_blog_root() -> Path:
    candidates: list[Path] = []
    configured = os.environ.get("TOOD_BLOG_ROOT")
    if configured:
        candidates.append(Path(configured))
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent)
    candidates.extend([Path.cwd(), Path(__file__).resolve().parent.parent])
    for candidate in candidates:
        for current in [candidate, *candidate.parents]:
            if (current / "config" / "_default" / "hugo.toml").is_file() and (current / "content").is_dir():
                return current.resolve()
    raise RuntimeError("未找到 Hugo 博客目录。请将 TOOD-Studio.exe 放在 myblog 根目录后重新打开。")


BLOG_ROOT = find_blog_root()
STATE_DIR = BLOG_ROOT / ".tood-studio"
STATE_DIR.mkdir(exist_ok=True)
LOG_FILE = STATE_DIR / "studio.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.update(MAX_CONTENT_LENGTH=12 * 1024 * 1024, JSON_AS_ASCII=False)
SESSION_TOKEN = uuid.uuid4().hex
preview_process: subprocess.Popen[str] | None = None
preview_url: str | None = None
operation_lock = threading.Lock()


def process_flags() -> dict[str, Any]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def command_environment() -> dict[str, str]:
    environment = os.environ.copy()
    try:
        index = int(environment.get("GIT_CONFIG_COUNT", "0"))
    except ValueError:
        index = 0
    environment["GIT_CONFIG_COUNT"] = str(index + 1)
    environment[f"GIT_CONFIG_KEY_{index}"] = "safe.directory"
    environment[f"GIT_CONFIG_VALUE_{index}"] = BLOG_ROOT.as_posix()
    return environment


def run_command(args: list[str], timeout: int = 120, cwd: Path = BLOG_ROOT) -> subprocess.CompletedProcess[str]:
    logging.info("run: %s", " ".join(args))
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=command_environment(),
        **process_flags(),
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "命令执行失败").strip()
        raise RuntimeError(message)
    return result


def tool_path(name: str) -> str:
    bundled = Path(getattr(sys, "_MEIPASS", "")) / "bin" / (f"{name}.exe" if os.name == "nt" else name)
    if bundled.is_file():
        return str(bundled)
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"未找到 {name}。请安装后重试。")
    return found


def git_args(*args: str) -> list[str]:
    return [tool_path("git"), "-c", f"safe.directory={BLOG_ROOT.as_posix()}", "-C", str(BLOG_ROOT), *args]


def load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_toml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = tomlkit.document()
    for key, value in data.items():
        document[key] = value
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(tomlkit.dumps(document), encoding="utf-8", newline="\n")
    temporary.replace(path)


def normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        values = value
    else:
        values = re.split(r"[,，\n]", str(value or ""))
    return [str(item).strip() for item in values if str(item).strip()]


def slugify(value: str) -> str:
    value = value.strip().lower().replace(" ", "-")
    value = re.sub(r"[^\w\-\u4e00-\u9fff]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-._")
    if not value:
        value = datetime.now().strftime("post-%Y%m%d-%H%M%S")
    return value[:100]


def post_path(slug: str) -> Path:
    safe_slug = slugify(slug)
    path = (BLOG_ROOT / "content" / "posts" / f"{safe_slug}.md").resolve()
    posts_root = (BLOG_ROOT / "content" / "posts").resolve()
    if path.parent != posts_root:
        raise ValueError("文章路径不安全")
    return path


def parse_post(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("+++"):
        end = text.find("\n+++", 3)
        if end >= 0:
            metadata = tomllib.loads(text[3:end].strip())
            body = text[end + 4 :].lstrip("\r\n")
            return metadata, body
    return {}, text


def serialize_post(metadata: dict[str, Any], body: str) -> str:
    frontmatter = tomlkit.dumps(metadata).strip()
    return f"+++\n{frontmatter}\n+++\n\n{body.rstrip()}\n"


def post_summary(path: Path) -> dict[str, Any]:
    metadata, body = parse_post(path)
    return {
        "slug": path.stem,
        "title": str(metadata.get("title") or path.stem),
        "date": str(metadata.get("date") or ""),
        "draft": bool(metadata.get("draft", True)),
        "description": str(metadata.get("description") or ""),
        "cover": str(metadata.get("cover") or ""),
        "categories": normalize_list(metadata.get("categories", [])),
        "tags": normalize_list(metadata.get("tags", [])),
        "words": len(re.findall(r"\S+", body)),
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
    }


def all_posts() -> list[dict[str, Any]]:
    posts_dir = BLOG_ROOT / "content" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    posts = [post_summary(path) for path in posts_dir.glob("*.md")]
    return sorted(posts, key=lambda item: (item["date"], item["modified"]), reverse=True)


def settings_payload() -> dict[str, Any]:
    data = load_toml(BLOG_ROOT / "data" / "site.toml")
    brand = data.get("brand", {})
    navigation = data.get("navigation", {})
    home = data.get("home", {})
    footer = data.get("footer", {})
    return {
        "brand_name": brand.get("name", "TOOD.WIN"),
        "brand_logo": brand.get("logo", ""),
        "archive_name": brand.get("archive_name", "TOOD ARCHIVE"),
        "nav_archives": navigation.get("archives", "归档"),
        "nav_categories": navigation.get("categories", "分类"),
        "nav_tags": navigation.get("tags", "标签"),
        "nav_about": navigation.get("about", "关于"),
        "nav_index": navigation.get("index", "INDEX"),
        "hero_primary": home.get("hero_primary", "TOOD"),
        "hero_secondary": home.get("hero_secondary", "ARCHIVE"),
        "tagline": home.get("tagline", ""),
        "build_label": home.get("build_label", "BUILD YOUR OWN ARCHIVE."),
        "about_title": home.get("about_title", "ABOUT"),
        "about_text": home.get("about_text", ""),
        "about_link_label": home.get("about_link_label", "了解更多 →"),
        "established_date": home.get("established_date", ""),
        "copyright_since": footer.get("copyright_since", datetime.now().year),
        "footer_build_label": footer.get("build_label", "BUILT WITH HUGO"),
    }


def write_settings(values: dict[str, Any]) -> None:
    limited = {key: str(value).strip()[:500] for key, value in values.items() if value is not None}
    data = {
        "brand": {
            "name": limited.get("brand_name", "TOOD.WIN"),
            "logo": limited.get("brand_logo", ""),
            "archive_name": limited.get("archive_name", "TOOD ARCHIVE"),
        },
        "navigation": {
            "archives": limited.get("nav_archives", "归档"),
            "categories": limited.get("nav_categories", "分类"),
            "tags": limited.get("nav_tags", "标签"),
            "about": limited.get("nav_about", "关于"),
            "index": limited.get("nav_index", "INDEX"),
        },
        "home": {
            "hero_primary": limited.get("hero_primary", "TOOD"),
            "hero_secondary": limited.get("hero_secondary", "ARCHIVE"),
            "tagline": limited.get("tagline", ""),
            "build_label": limited.get("build_label", "BUILD YOUR OWN ARCHIVE."),
            "about_title": limited.get("about_title", "ABOUT"),
            "about_text": limited.get("about_text", ""),
            "about_link_label": limited.get("about_link_label", "了解更多 →"),
            "established_date": limited.get("established_date", ""),
        },
        "footer": {
            "copyright_since": int(values.get("copyright_since") or datetime.now().year),
            "build_label": limited.get("footer_build_label", "BUILT WITH HUGO"),
        },
    }
    save_toml(BLOG_ROOT / "data" / "site.toml", data)


def free_port(start: int = 1413) -> int:
    for port in range(start, start + 50):
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("没有可用的本地预览端口")


def stop_preview() -> None:
    global preview_process, preview_url
    if preview_process and preview_process.poll() is None:
        preview_process.terminate()
        try:
            preview_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            preview_process.kill()
    preview_process = None
    preview_url = None


atexit.register(stop_preview)


@app.before_request
def verify_local_request():
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"ok": False, "error": "只允许本机访问"}), 403
    if request.method in WRITE_METHODS and request.headers.get("X-TOOD-Token") != SESSION_TOKEN:
        return jsonify({"ok": False, "error": "请求令牌无效"}), 403
    return None


@app.errorhandler(Exception)
def handle_error(error: Exception):
    logging.exception("request failed")
    return jsonify({"ok": False, "error": str(error)}), 400


@app.get("/favicon.ico")
def favicon():
    return "", 204


@app.get("/")
def index():
    return render_template("index.html", token=SESSION_TOKEN, version=APP_VERSION, blog_root=str(BLOG_ROOT))


@app.get("/api/status")
def api_status():
    branch = run_command(git_args("branch", "--show-current"), timeout=15).stdout.strip()
    ignored_prefixes = ("public/", "resources/", ".hugo_build.lock")
    changes = [
        line for line in run_command(git_args("status", "--porcelain"), timeout=15).stdout.splitlines()
        if not line[3:].replace("\\", "/").startswith(ignored_prefixes)
    ]
    versions: dict[str, str] = {}
    for name in ("hugo", "git"):
        try:
            command = [tool_path(name), "version" if name == "hugo" else "--version"]
            versions[name] = run_command(command, timeout=15).stdout.strip()
        except Exception as exc:
            versions[name] = str(exc)
    return jsonify({
        "ok": True,
        "app": APP_NAME,
        "version": APP_VERSION,
        "root": str(BLOG_ROOT),
        "branch": branch,
        "changes": len(changes),
        "preview_url": preview_url,
        "tools": versions,
    })


@app.get("/api/settings")
def api_get_settings():
    return jsonify({"ok": True, "settings": settings_payload()})


@app.post("/api/settings")
def api_save_settings():
    write_settings(request.get_json(force=True) or {})
    return jsonify({"ok": True, "message": "网站设置已保存"})


@app.get("/api/posts")
def api_posts():
    return jsonify({"ok": True, "posts": all_posts()})


@app.get("/api/posts/<slug>")
def api_get_post(slug: str):
    path = post_path(slug)
    if not path.is_file():
        raise FileNotFoundError("文章不存在")
    metadata, body = parse_post(path)
    item = post_summary(path)
    item["body"] = body
    item["date"] = str(metadata.get("date") or "")
    return jsonify({"ok": True, "post": item})


@app.post("/api/posts")
def api_save_post():
    payload = request.get_json(force=True) or {}
    title = str(payload.get("title") or "").strip()
    if not title:
        raise ValueError("文章标题不能为空")
    original_slug = str(payload.get("original_slug") or "").strip()
    slug = slugify(str(payload.get("slug") or title))
    path = post_path(slug)
    if path.exists() and original_slug and original_slug != slug:
        raise FileExistsError("新的文章 URL 已存在")
    date_value = str(payload.get("date") or datetime.now().astimezone().isoformat(timespec="seconds"))
    parsed_date = datetime.fromisoformat(date_value)
    if parsed_date.tzinfo is None:
        parsed_date = parsed_date.astimezone()
    date_value = parsed_date.isoformat(timespec="seconds")
    existing_path = post_path(original_slug) if original_slug else path
    metadata = parse_post(existing_path)[0] if existing_path.is_file() else {}
    metadata.update({
        "title": title[:200],
        "date": date_value,
        "draft": bool(payload.get("draft", True)),
    })
    description = str(payload.get("description") or "").strip()
    if description:
        metadata["description"] = description[:500]
    else:
        metadata.pop("description", None)
    cover = str(payload.get("cover") or "").strip()
    if cover:
        metadata["cover"] = cover[:1000]
    else:
        metadata.pop("cover", None)
    categories = normalize_list(payload.get("categories", []))
    tags = normalize_list(payload.get("tags", []))
    if categories:
        metadata["categories"] = categories
    else:
        metadata.pop("categories", None)
    if tags:
        metadata["tags"] = tags
    else:
        metadata.pop("tags", None)
    body = str(payload.get("body") or "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_post(metadata, body), encoding="utf-8", newline="\n")
    if original_slug and original_slug != slug:
        old_path = post_path(original_slug)
        if old_path.is_file():
            old_path.unlink()
    state = "草稿，不会显示在线" if metadata["draft"] else "公开文章"
    return jsonify({"ok": True, "message": f"文章已保存为{state}", "slug": slug})


@app.delete("/api/posts/<slug>")
def api_delete_post(slug: str):
    path = post_path(slug)
    if not path.is_file():
        raise FileNotFoundError("文章不存在")
    trash = STATE_DIR / "trash" / "posts"
    trash.mkdir(parents=True, exist_ok=True)
    destination = trash / f"{datetime.now():%Y%m%d-%H%M%S}-{path.name}"
    shutil.move(str(path), destination)
    return jsonify({"ok": True, "message": "文章已移入回收站"})


@app.post("/api/markdown")
def api_markdown():
    body = str((request.get_json(force=True) or {}).get("body") or "")
    html = markdown.markdown(body, extensions=["fenced_code", "tables", "sane_lists"])
    return jsonify({"ok": True, "html": html})


@app.post("/api/upload")
def api_upload():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        raise ValueError("请选择图片")
    suffix = Path(uploaded.filename).suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        raise ValueError("仅支持 PNG、JPG、WEBP 和 GIF 图片")
    base = secure_filename(Path(uploaded.filename).stem) or "image"
    folder = BLOG_ROOT / "static" / "uploads" / datetime.now().strftime("%Y/%m")
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{base}-{uuid.uuid4().hex[:8]}{suffix}"
    target = folder / filename
    uploaded.save(target)
    url = "/" + target.relative_to(BLOG_ROOT / "static").as_posix()
    return jsonify({"ok": True, "url": url, "markdown": f"![{base}]({url})"})


@app.post("/api/logo")
def api_logo():
    result = api_upload().get_json()
    settings = settings_payload()
    settings["brand_logo"] = result["url"]
    write_settings(settings)
    return jsonify({"ok": True, "url": result["url"], "message": "Logo 已上传并保存"})


@app.post("/api/preview")
def api_preview():
    global preview_process, preview_url
    with operation_lock:
        if preview_process and preview_process.poll() is None:
            return jsonify({"ok": True, "url": preview_url})
        port = free_port()
        command = [
            tool_path("hugo"), "server", "--source", str(BLOG_ROOT), "--bind", "127.0.0.1",
            "--port", str(port), "--disableFastRender", "--buildDrafts", "--renderToMemory",
            "--enableGitInfo=false",
        ]
        log_handle = (STATE_DIR / "hugo-preview.log").open("w", encoding="utf-8")
        preview_process = subprocess.Popen(
            command,
            cwd=BLOG_ROOT,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            env=command_environment(),
            **process_flags(),
        )
        preview_url = f"http://127.0.0.1:{port}/"
        time.sleep(1)
        if preview_process.poll() is not None:
            raise RuntimeError((STATE_DIR / "hugo-preview.log").read_text(encoding="utf-8", errors="replace"))
    return jsonify({"ok": True, "url": preview_url})


@app.post("/api/build")
def api_build():
    with operation_lock, tempfile.TemporaryDirectory(prefix="tood-build-") as destination:
        result = run_command([
            tool_path("hugo"), "--source", str(BLOG_ROOT), "--destination", destination,
            "--cleanDestinationDir", "--enableGitInfo=false",
        ], timeout=180)
    return jsonify({"ok": True, "message": "Hugo 构建检查通过", "output": result.stdout[-4000:]})


@app.post("/api/publish")
def api_publish():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message") or f"content: publish via TOOD Studio {datetime.now():%Y-%m-%d %H:%M}")[:180]
    with operation_lock, tempfile.TemporaryDirectory(prefix="tood-publish-") as destination:
        build = run_command([
            tool_path("hugo"), "--source", str(BLOG_ROOT), "--destination", destination,
            "--cleanDestinationDir", "--enableGitInfo=false",
        ], timeout=180)
        managed = ["content", "data/site.toml", "static/uploads"]
        existing = [item for item in managed if (BLOG_ROOT / item).exists()]
        run_command(git_args("add", "--", *existing), timeout=30)
        staged = subprocess.run(
            git_args("diff", "--cached", "--quiet"), cwd=BLOG_ROOT, timeout=30, **process_flags()
        ).returncode
        committed = staged != 0
        if committed:
            run_command(git_args("commit", "-m", message), timeout=60)

        push: subprocess.CompletedProcess[str] | None = None
        last_error: RuntimeError | None = None
        for delay in (0, 2, 5):
            if delay:
                time.sleep(delay)
            try:
                push = run_command(git_args("push", "origin", "HEAD"), timeout=180)
                break
            except RuntimeError as error:
                last_error = error
                logging.warning("git push failed, will retry: %s", error)
        if push is None:
            raise last_error or RuntimeError("GitHub 推送失败")

    action = "内容已提交并推送" if committed else "GitHub 已确认同步"
    return jsonify({
        "ok": True,
        "message": f"{action}到 GitHub，Cloudflare 将自动部署",
        "output": (push.stdout + push.stderr) or build.stdout[-2000:],
    })


@app.post("/api/shutdown")
def api_shutdown():
    def exit_later():
        time.sleep(0.3)
        stop_preview()
        os._exit(0)
    threading.Thread(target=exit_later, daemon=True).start()
    return jsonify({"ok": True, "message": "TOOD Studio 已退出"})


def find_app_port() -> int:
    return free_port(43117)


def hide_windows_console() -> None:
    if os.name != "nt" or not getattr(sys, "frozen", False) or os.environ.get("TOOD_STUDIO_SHOW_CONSOLE") == "1":
        return
    try:
        import ctypes
        console = ctypes.windll.kernel32.GetConsoleWindow()
        if console:
            ctypes.windll.user32.ShowWindow(console, 0)
    except Exception:
        logging.exception("could not hide console")


def main() -> None:
    hide_windows_console()
    port = find_app_port()
    url = f"http://127.0.0.1:{port}/"
    if os.environ.get("TOOD_STUDIO_NO_BROWSER") != "1":
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    logging.info("TOOD Studio %s started at %s for %s", APP_VERSION, url, BLOG_ROOT)
    serve(app, host="127.0.0.1", port=port, threads=6, channel_timeout=300)


if __name__ == "__main__":
    main()
