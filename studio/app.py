from __future__ import annotations

import atexit
import base64
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
from urllib import error as urlerror
from urllib import request as urlrequest
from datetime import datetime
from pathlib import Path
from typing import Any

import markdown
import tomlkit
from flask import Flask, jsonify, render_template, request
from waitress import serve
from werkzeug.utils import secure_filename


APP_NAME = "TOOD Studio"
APP_VERSION = "1.3.8"
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}


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
            for possible_root in (current, current / "myblog"):
                if (possible_root / "config" / "_default" / "hugo.toml").is_file() and (possible_root / "content").is_dir():
                    return possible_root.resolve()
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


def git_text(*args: str, timeout: int = 30) -> str:
    return run_command(git_args(*args), timeout=timeout).stdout.strip()


def github_settings_path() -> Path:
    return BLOG_ROOT / ".tood-studio" / "github.json"


def load_github_settings() -> dict[str, Any]:
    path = github_settings_path()
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def normalize_github_repository(value: str) -> tuple[str, str]:
    repository = value.strip()
    if repository.startswith("git@github.com:"):
        repository = repository.split(":", 1)[1]
    else:
        repository = re.sub(r"^https?://github\.com/", "", repository, flags=re.IGNORECASE)
    repository = repository.removesuffix(".git").strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("GitHub 仓库格式无效，请填写 owner/repository 或完整仓库地址")
    return repository, f"https://github.com/{repository}.git"


def github_connection_payload() -> dict[str, Any]:
    settings = load_github_settings()
    repository = str(settings.get("repository") or "")
    branch = str(settings.get("branch") or "main")
    user_name = str(settings.get("user_name") or "")
    user_email = str(settings.get("user_email") or "")
    return {
        "repository": repository,
        "branch": branch,
        "user_name": user_name,
        "user_email": user_email,
        "token_configured": bool(settings.get("token")),
        "connected": bool(repository and user_name and user_email and settings.get("token")),
    }


def configure_github_connection(payload: dict[str, Any]) -> dict[str, Any]:
    repository, remote_url = normalize_github_repository(str(payload.get("repository") or ""))
    branch = str(payload.get("branch") or "main").strip()
    user_name = str(payload.get("user_name") or "").strip()
    user_email = str(payload.get("user_email") or "").strip()
    current = load_github_settings()
    token = str(payload.get("token") or current.get("token") or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", branch) or ".." in branch or branch.startswith("/") or branch.endswith("/"):
        raise ValueError("Git 分支名称无效")
    if not user_name:
        raise ValueError("请填写 Git 提交用户名")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", user_email):
        raise ValueError("请填写有效的 Git 提交邮箱")
    if not token:
        raise ValueError("首次连接需要填写 GitHub Personal Access Token")

    repository_info = github_request(repository, token, "GET", "")
    github_request(repository, token, "GET", f"/git/ref/heads/{branch}")

    remotes = git_text("remote").splitlines()
    if "origin" in remotes:
        run_command(git_args("remote", "set-url", "origin", remote_url), timeout=15)
    else:
        run_command(git_args("remote", "add", "origin", remote_url), timeout=15)
    run_command(git_args("config", "user.name", user_name), timeout=15)
    run_command(git_args("config", "user.email", user_email), timeout=15)
    current_branch = git_text("branch", "--show-current")
    if current_branch and current_branch != branch:
        run_command(git_args("branch", "-M", branch), timeout=15)

    path = github_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({
        "repository": repository,
        "branch": branch,
        "user_name": user_name,
        "user_email": user_email,
        "token": token,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(temporary, 0o600)
    except OSError:
        pass
    temporary.replace(path)
    return {
        "repository": repository,
        "branch": branch,
        "user_name": user_name,
        "user_email": user_email,
        "token_configured": True,
        "connected": True,
        "repository_name": str(repository_info.get("full_name") or repository),
    }


def github_repository() -> str:
    remote = git_text("remote", "get-url", "origin")
    if remote.startswith("git@github.com:"):
        repository = remote.split(":", 1)[1]
    else:
        match = re.match(r"https?://github\.com/(.+)$", remote)
        if not match:
            raise RuntimeError("当前 origin 不是 GitHub 仓库地址")
        repository = match.group(1)
    return repository.removesuffix(".git").strip("/")


def github_token() -> str:
    configured = str(load_github_settings().get("token") or "").strip()
    if configured:
        return configured
    result = subprocess.run(
        [tool_path("git"), "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
        env=command_environment(),
        **process_flags(),
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "无法读取 GitHub 登录凭据").strip())
    credentials = dict(
        line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
    )
    token = credentials.get("password", "")
    if not token:
        raise RuntimeError("未找到 GitHub 登录凭据，请先在 Git Credential Manager 中登录")
    return token


def github_request(
    repository: str,
    token: str,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request_object = urlrequest.Request(
        f"https://api.github.com/repos/{repository}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "TOOD-Studio",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlrequest.urlopen(request_object, timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))
    except urlerror.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(detail).get("message", detail)
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"GitHub API 返回 {error.code}：{detail}") from error
    except urlerror.URLError as error:
        raise RuntimeError(f"无法连接 GitHub API：{error.reason}") from error


def git_blob_bytes(sha: str) -> bytes:
    result = subprocess.run(
        git_args("cat-file", "blob", sha),
        cwd=BLOG_ROOT,
        capture_output=True,
        timeout=30,
        env=command_environment(),
        **process_flags(),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def write_commit_object(raw_commit: str) -> str:
    result = subprocess.run(
        git_args("hash-object", "-t", "commit", "-w", "--stdin"),
        input=raw_commit.encode("utf-8"),
        cwd=BLOG_ROOT,
        capture_output=True,
        timeout=30,
        env=command_environment(),
        **process_flags(),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout.decode("ascii").strip()


def commit_metadata(commit: str) -> dict[str, str]:
    marker = "%x00"
    output = run_command(
        git_args(
            "show", "-s",
            f"--format=%an{marker}%ae{marker}%at{marker}%aI{marker}%cn{marker}%ce{marker}%ct{marker}%cI{marker}%B",
            commit,
        ),
        timeout=30,
    ).stdout
    values = output.split("\x00", 8)
    if len(values) != 9:
        raise RuntimeError("无法读取本地提交信息")
    keys = (
        "author_name", "author_email", "author_epoch", "author_iso",
        "committer_name", "committer_email", "committer_epoch", "committer_iso", "message",
    )
    metadata = dict(zip(keys, values))
    metadata["message"] = metadata["message"].rstrip("\r\n")
    return metadata


def commit_changes(parent: str, commit: str, repository: str, token: str) -> list[dict[str, Any]]:
    output = git_text(
        "-c", "core.quotepath=false",
        "diff-tree", "--no-commit-id", "--name-status", "-r", "-M", parent, commit,
    )
    entries: list[dict[str, Any]] = []
    blob_cache: dict[str, str] = {}
    for line in output.splitlines():
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R"):
            entries.append({"path": parts[1], "mode": "100644", "type": "blob", "sha": None})
            path = parts[2]
        elif status == "D":
            entries.append({"path": parts[1], "mode": "100644", "type": "blob", "sha": None})
            continue
        else:
            path = parts[1]

        tree_line = git_text("ls-tree", commit, "--", path)
        tree_info = tree_line.split("\t", 1)[0].split()
        if len(tree_info) != 3 or tree_info[1] != "blob":
            raise RuntimeError(f"暂不支持发布此 Git 对象：{path}")
        mode, object_type, local_blob = tree_info
        if local_blob not in blob_cache:
            blob = github_request(
                repository,
                token,
                "POST",
                "/git/blobs",
                {"content": base64.b64encode(git_blob_bytes(local_blob)).decode("ascii"), "encoding": "base64"},
            )
            blob_cache[local_blob] = str(blob["sha"])
        entries.append({"path": path, "mode": mode, "type": object_type, "sha": blob_cache[local_blob]})
    return entries


def push_with_github_api() -> str:
    repository = github_repository()
    token = github_token()
    branch = git_text("symbolic-ref", "--short", "HEAD")
    local_head = git_text("rev-parse", "HEAD")
    remote_ref = github_request(repository, token, "GET", f"/git/ref/heads/{branch}")
    remote_head = str(remote_ref["object"]["sha"])
    if remote_head == local_head:
        run_command(git_args("update-ref", f"refs/remotes/origin/{branch}", remote_head), timeout=15)
        return "GitHub 已是最新状态，无需重复推送"

    known_remote = subprocess.run(
        git_args("cat-file", "-e", f"{remote_head}^{{commit}}"),
        cwd=BLOG_ROOT,
        timeout=15,
        env=command_environment(),
        **process_flags(),
    ).returncode == 0
    if not known_remote:
        raise RuntimeError("GitHub 上存在本地尚未同步的提交，请先更新本地仓库")
    is_ancestor = subprocess.run(
        git_args("merge-base", "--is-ancestor", remote_head, local_head),
        cwd=BLOG_ROOT,
        timeout=15,
        env=command_environment(),
        **process_flags(),
    ).returncode == 0
    if not is_ancestor:
        raise RuntimeError("GitHub 与本地提交历史已分叉，请先处理同步冲突")

    commits = git_text("rev-list", "--reverse", f"{remote_head}..{local_head}").splitlines()
    api_parent = remote_head
    final_sha = remote_head
    for commit in commits:
        local_parent = git_text("rev-parse", f"{commit}^")
        local_tree = git_text("rev-parse", f"{commit}^{{tree}}")
        entries = commit_changes(local_parent, commit, repository, token)
        api_tree = github_request(
            repository,
            token,
            "POST",
            "/git/trees",
            {"base_tree": api_parent, "tree": entries},
        )
        if api_tree["sha"] != local_tree:
            raise RuntimeError("GitHub 生成的文件树与本地不一致，已停止发布")
        metadata = commit_metadata(commit)
        api_commit = github_request(
            repository,
            token,
            "POST",
            "/git/commits",
            {
                "message": metadata["message"],
                "tree": local_tree,
                "parents": [api_parent],
                "author": {
                    "name": metadata["author_name"],
                    "email": metadata["author_email"],
                    "date": metadata["author_iso"],
                },
                "committer": {
                    "name": metadata["committer_name"],
                    "email": metadata["committer_email"],
                    "date": metadata["committer_iso"],
                },
            },
        )
        author_zone = metadata["author_iso"][-6:].replace(":", "")
        committer_zone = metadata["committer_iso"][-6:].replace(":", "")
        raw_commit = (
            f"tree {local_tree}\nparent {api_parent}\n"
            f"author {metadata['author_name']} <{metadata['author_email']}> {metadata['author_epoch']} {author_zone}\n"
            f"committer {metadata['committer_name']} <{metadata['committer_email']}> {metadata['committer_epoch']} {committer_zone}\n\n"
            f"{metadata['message']}"
        )
        written_sha = write_commit_object(raw_commit)
        if written_sha != api_commit["sha"]:
            raise RuntimeError("GitHub 提交校验失败，已停止更新本地分支")
        api_parent = str(api_commit["sha"])
        final_sha = api_parent

    github_request(
        repository,
        token,
        "PATCH",
        f"/git/refs/heads/{branch}",
        {"sha": final_sha, "force": False},
    )
    run_command(git_args("update-ref", f"refs/heads/{branch}", final_sha, local_head), timeout=15)
    run_command(git_args("update-ref", f"refs/remotes/origin/{branch}", final_sha, remote_head), timeout=15)
    return f"已通过 GitHub API 发布 {len(commits)} 个提交"


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


def bounded_int(value: Any, default: int, minimum: int = 1, maximum: int = 20) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def boolean_value(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off", ""}:
        return False
    return default


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
        "featured": bool(metadata.get("featured", False)),
        "showArticleExtras": bool(metadata.get("showArticleExtras", True)),
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


def internal_post_link_pattern(slug: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?P<prefix>(?:https?://[^/\s)\"']+)?/posts/){re.escape(slug)}"
        r"(?P<suffix>/?(?=[?#\s)\"']|$))",
        flags=re.IGNORECASE,
    )


def post_references(slug: str) -> list[dict[str, Any]]:
    pattern = internal_post_link_pattern(slug)
    references = []
    for path in (BLOG_ROOT / "content" / "posts").glob("*.md"):
        if path.stem == slug:
            continue
        _, body = parse_post(path)
        if pattern.search(body):
            references.append(post_summary(path))
    return sorted(references, key=lambda item: item["title"].casefold())


def update_internal_post_links(old_slug: str, new_slug: str) -> int:
    pattern = internal_post_link_pattern(old_slug)
    updated = 0
    for path in (BLOG_ROOT / "content" / "posts").glob("*.md"):
        if path.stem == old_slug:
            continue
        metadata, body = parse_post(path)
        new_body, replacements = pattern.subn(
            lambda match: f"{match.group('prefix')}{new_slug}{match.group('suffix')}",
            body,
        )
        if replacements:
            path.write_text(serialize_post(metadata, new_body), encoding="utf-8", newline="\n")
            updated += 1
    return updated


def settings_payload() -> dict[str, Any]:
    data = load_toml(BLOG_ROOT / "data" / "site.toml")
    brand = data.get("brand", {})
    navigation = data.get("navigation", {})
    home = data.get("home", {})
    footer = data.get("footer", {})
    seo = data.get("seo", {})
    return {
        "brand_name": brand.get("name", "TOOD.WIN"),
        "brand_logo": brand.get("logo", ""),
        "browser_title": brand.get("browser_title", brand.get("name", "TOOD.WIN")),
        "favicon": brand.get("favicon", ""),
        "archive_name": brand.get("archive_name", "TOOD ARCHIVE"),
        "nav_archives": navigation.get("archives", "归档"),
        "nav_categories": navigation.get("categories", "分类"),
        "nav_tags": navigation.get("tags", "标签"),
        "nav_about": navigation.get("about", "关于"),
        "nav_index": navigation.get("index", "INDEX"),
        "hero_primary": home.get("hero_primary", "TOOD"),
        "hero_secondary": home.get("hero_secondary", "ARCHIVE"),
        "tagline": home.get("tagline", ""),
        "hero_visible": boolean_value(home.get("hero_visible"), True),
        "hero_title_size": bounded_int(home.get("hero_title_size"), 60, 28, 96),
        "hero_tagline_size": bounded_int(home.get("hero_tagline_size"), 17, 12, 32),
        "build_label": home.get("build_label", "BUILD YOUR OWN ARCHIVE."),
        "about_title": home.get("about_title", "ABOUT"),
        "about_text": home.get("about_text", ""),
        "about_link_label": home.get("about_link_label", "了解更多 →"),
        "established_date": home.get("established_date", ""),
        "latest_articles_count": bounded_int(home.get("latest_articles_count"), 5),
        "quarter_random_count": bounded_int(home.get("quarter_random_count"), 5),
        "copyright_since": footer.get("copyright_since", datetime.now().year),
        "footer_build_label": footer.get("build_label", "BUILT WITH HUGO"),
        "seo_description": seo.get("description", ""),
        "seo_keywords": seo.get("keywords", ""),
    }


def write_settings(values: dict[str, Any]) -> None:
    limited = {key: str(value).strip()[:500] for key, value in values.items() if value is not None}
    current = load_toml(BLOG_ROOT / "data" / "site.toml")
    data = {
        "brand": {
            "name": limited.get("brand_name", "TOOD.WIN"),
            "logo": limited.get("brand_logo", ""),
            "browser_title": limited.get("browser_title", limited.get("brand_name", "TOOD.WIN")),
            "favicon": limited.get("favicon", ""),
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
            "hero_visible": boolean_value(values.get("hero_visible"), True),
            "hero_title_size": bounded_int(values.get("hero_title_size"), 60, 28, 96),
            "hero_tagline_size": bounded_int(values.get("hero_tagline_size"), 17, 12, 32),
            "build_label": limited.get("build_label", "BUILD YOUR OWN ARCHIVE."),
            "about_title": limited.get("about_title", "ABOUT"),
            "about_text": limited.get("about_text", ""),
            "about_link_label": limited.get("about_link_label", "了解更多 →"),
            "established_date": limited.get("established_date", ""),
            "latest_articles_count": bounded_int(values.get("latest_articles_count"), 5),
            "quarter_random_count": bounded_int(values.get("quarter_random_count"), 5),
        },
        "footer": {
            "copyright_since": int(values.get("copyright_since") or datetime.now().year),
            "build_label": limited.get("footer_build_label", "BUILT WITH HUGO"),
        },
        "seo": {
            "description": limited.get("seo_description", ""),
            "keywords": limited.get("seo_keywords", ""),
        },
        "advertising": current.get("advertising", {}),
    }
    save_toml(BLOG_ROOT / "data" / "site.toml", data)


def advertising_payload() -> dict[str, Any]:
    data = load_toml(BLOG_ROOT / "data" / "site.toml").get("advertising", {})
    return {
        "google_ads_code": str(data.get("google_ads_code") or ""),
        "home_sidebar_enabled": boolean_value(data.get("home_sidebar_enabled"), False),
        "home_sidebar_code": str(data.get("home_sidebar_code") or ""),
        "article_content_enabled": boolean_value(data.get("article_content_enabled"), False),
        "article_content_code": str(data.get("article_content_code") or ""),
        "article_sidebar_enabled": boolean_value(data.get("article_sidebar_enabled"), False),
        "article_sidebar_code": str(data.get("article_sidebar_code") or ""),
    }


def write_advertising(values: dict[str, Any]) -> None:
    path = BLOG_ROOT / "data" / "site.toml"
    data = load_toml(path)
    data["advertising"] = {
        "google_ads_code": str(values.get("google_ads_code") or "").strip()[:20000],
        "home_sidebar_enabled": boolean_value(values.get("home_sidebar_enabled"), False),
        "home_sidebar_code": str(values.get("home_sidebar_code") or "").strip()[:30000],
        "article_content_enabled": boolean_value(values.get("article_content_enabled"), False),
        "article_content_code": str(values.get("article_content_code") or "").strip()[:30000],
        "article_sidebar_enabled": boolean_value(values.get("article_sidebar_enabled"), False),
        "article_sidebar_code": str(values.get("article_sidebar_code") or "").strip()[:30000],
    }
    save_toml(path, data)


def taxonomy_catalog_path() -> Path:
    return BLOG_ROOT / "data" / "taxonomies.toml"


def category_settings_path() -> Path:
    return BLOG_ROOT / "data" / "category_settings.toml"


def category_settings() -> dict[str, dict[str, bool]]:
    data = load_toml(category_settings_path()).get("categories", {})
    if not isinstance(data, dict):
        return {}
    return {
        str(name): {
            "show_on_home": boolean_value(values.get("show_on_home"), True),
            "show_in_archives": boolean_value(values.get("show_in_archives"), True),
        }
        for name, values in data.items()
        if isinstance(values, dict)
    }


def save_category_settings(settings: dict[str, dict[str, bool]]) -> None:
    save_toml(category_settings_path(), {"categories": settings})


def category_display(name: str) -> dict[str, bool]:
    settings = category_settings()
    matched = next((values for label, values in settings.items() if label.casefold() == name.casefold()), None)
    return matched or {"show_on_home": True, "show_in_archives": True}


def set_category_display(name: str, values: dict[str, Any]) -> None:
    settings = category_settings()
    existing = next((label for label in settings if label.casefold() == name.casefold()), name)
    current = category_display(name)
    settings[existing] = {
        "show_on_home": boolean_value(values.get("show_on_home"), current["show_on_home"]),
        "show_in_archives": boolean_value(values.get("show_in_archives"), current["show_in_archives"]),
    }
    save_category_settings(settings)


def taxonomy_catalog() -> dict[str, list[str]]:
    data = load_toml(taxonomy_catalog_path())
    return {
        "categories": normalize_list(data.get("categories", [])),
        "tags": normalize_list(data.get("tags", [])),
    }


def save_taxonomy_catalog(catalog: dict[str, list[str]]) -> None:
    save_toml(taxonomy_catalog_path(), {
        "categories": sorted(dict.fromkeys(catalog.get("categories", [])), key=str.casefold),
        "tags": sorted(dict.fromkeys(catalog.get("tags", [])), key=str.casefold),
    })


def validate_taxonomy(kind: str, name: Any) -> str:
    if kind not in {"categories", "tags"}:
        raise ValueError("分类或标签类型无效")
    value = str(name or "").strip()
    if not value:
        raise ValueError("名称不能为空")
    if len(value) > 80:
        raise ValueError("名称不能超过 80 个字符")
    if any(character in value for character in "\r\n,"):
        raise ValueError("名称不能包含换行或逗号")
    return value


def ensure_taxonomy_values(kind: str, values: list[str]) -> None:
    if not values:
        return
    catalog = taxonomy_catalog()
    known = {item.casefold() for item in catalog[kind]}
    changed = False
    for value in values:
        if value.casefold() not in known:
            catalog[kind].append(value)
            known.add(value.casefold())
            changed = True
    if changed:
        save_taxonomy_catalog(catalog)


def taxonomy_payload() -> dict[str, list[dict[str, Any]]]:
    catalog = taxonomy_catalog()
    counts: dict[str, dict[str, int]] = {"categories": {}, "tags": {}}
    labels: dict[str, dict[str, str]] = {"categories": {}, "tags": {}}
    for path in sorted((BLOG_ROOT / "content" / "posts").glob("*.md")):
        metadata, _ = parse_post(path)
        for kind in ("categories", "tags"):
            for value in normalize_list(metadata.get(kind, [])):
                key = value.casefold()
                labels[kind].setdefault(key, value)
                counts[kind][key] = counts[kind].get(key, 0) + 1
    result: dict[str, list[dict[str, Any]]] = {}
    for kind in ("categories", "tags"):
        for value in catalog[kind]:
            labels[kind].setdefault(value.casefold(), value)
        result[kind] = []
        for key, label in sorted(labels[kind].items(), key=lambda item: item[1].casefold()):
            item = {"name": label, "count": counts[kind].get(key, 0)}
            if kind == "categories":
                item.update(category_display(label))
            result[kind].append(item)
    return result


def replace_taxonomy_value(kind: str, old_name: str, new_name: str | None) -> int:
    old_key = old_name.casefold()
    changed_posts = 0
    for path in sorted((BLOG_ROOT / "content" / "posts").glob("*.md")):
        metadata, body = parse_post(path)
        values = normalize_list(metadata.get(kind, []))
        if not any(value.casefold() == old_key for value in values):
            continue
        replacement: list[str] = []
        for value in values:
            candidate = new_name if value.casefold() == old_key else value
            if candidate and candidate.casefold() not in {item.casefold() for item in replacement}:
                replacement.append(candidate)
        if replacement:
            metadata[kind] = replacement
        else:
            metadata.pop(kind, None)
        path.write_text(serialize_post(metadata, body), encoding="utf-8", newline="\n")
        changed_posts += 1

    catalog = taxonomy_catalog()
    catalog[kind] = [value for value in catalog[kind] if value.casefold() != old_key]
    if new_name and new_name.casefold() not in {value.casefold() for value in catalog[kind]}:
        catalog[kind].append(new_name)
    save_taxonomy_catalog(catalog)
    if kind == "categories":
        settings = category_settings()
        matched = next((label for label in settings if label.casefold() == old_key), None)
        if matched:
            display = settings.pop(matched)
            if new_name:
                settings[new_name] = display
            save_category_settings(settings)
    return changed_posts


def about_page_path() -> Path:
    return BLOG_ROOT / "content" / "page" / "about" / "index.zh.md"


def parse_about_page() -> dict[str, str]:
    path = about_page_path()
    if not path.is_file():
        raise FileNotFoundError("未找到中文关于页面")
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", text, re.DOTALL)
    if not match:
        raise ValueError("关于页面 Front Matter 格式无效")
    header, body = match.groups()

    def field(name: str) -> str:
        item = re.search(rf"(?m)^{re.escape(name)}:\s*(.*?)\s*$", header)
        if not item:
            return ""
        value = item.group(1).strip()
        if value.startswith(('"', "'")):
            try:
                return str(json.loads(value))
            except json.JSONDecodeError:
                return value.strip("\"'")
        return value

    return {"title": field("title"), "description": field("description"), "body": body.rstrip()}


def write_about_page(values: dict[str, Any]) -> None:
    path = about_page_path()
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", text, re.DOTALL)
    if not match:
        raise ValueError("关于页面 Front Matter 格式无效")
    header = match.group(1)
    title = str(values.get("title") or "").strip()[:200]
    if not title:
        raise ValueError("关于页面标题不能为空")
    description = str(values.get("description") or "").strip()[:500]
    body = str(values.get("body") or "")

    def replace_field(source: str, name: str, value: str) -> str:
        rendered = f"{name}: {json.dumps(value, ensure_ascii=False)}"
        pattern = rf"(?m)^{re.escape(name)}:\s*.*$"
        return re.sub(pattern, rendered, source, count=1) if re.search(pattern, source) else f"{rendered}\n{source}"

    header = replace_field(header, "title", title)
    header = replace_field(header, "description", description)
    header = replace_field(header, "lastmod", datetime.now().astimezone().date().isoformat())
    temporary = path.with_suffix(".md.tmp")
    temporary.write_text(f"---\n{header}\n---\n\n{body.rstrip()}\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def friend_links_path() -> Path:
    return BLOG_ROOT / "data" / "friends.toml"


def friends_payload() -> dict[str, Any]:
    data = load_toml(friend_links_path())
    settings = data.get("settings", {})
    links = data.get("links", [])
    return {
        "homepage_enabled": boolean_value(settings.get("homepage_enabled"), True),
        "homepage_limit": bounded_int(settings.get("homepage_limit"), 5, 1, 20),
        "links": [
            {
                "name": str(item.get("name") or ""),
                "url": str(item.get("url") or ""),
                "description": str(item.get("description") or ""),
                "logo": str(item.get("logo") or ""),
                "show_on_home": boolean_value(item.get("show_on_home"), True),
            }
            for item in links
            if isinstance(item, dict)
        ],
    }


def save_friend_links(values: dict[str, Any]) -> None:
    raw_links = values.get("links", [])
    if not isinstance(raw_links, list):
        raise ValueError("友情链接列表格式无效")
    links: list[dict[str, Any]] = []
    for raw_link in raw_links[:100]:
        if not isinstance(raw_link, dict):
            raise ValueError("友情链接条目格式无效")
        name = str(raw_link.get("name") or "").strip()[:100]
        url = str(raw_link.get("url") or "").strip()[:500]
        if not name:
            raise ValueError("友情链接名称不能为空")
        if not re.fullmatch(r"https?://[^\s]+", url, re.IGNORECASE):
            raise ValueError(f"“{name}”的网址必须以 http:// 或 https:// 开头")
        links.append({
            "name": name,
            "url": url,
            "description": str(raw_link.get("description") or "").strip()[:300],
            "logo": str(raw_link.get("logo") or "").strip()[:500],
            "show_on_home": boolean_value(raw_link.get("show_on_home"), True),
        })
    save_toml(friend_links_path(), {
        "settings": {
            "homepage_enabled": boolean_value(values.get("homepage_enabled"), True),
            "homepage_limit": bounded_int(values.get("homepage_limit"), 5, 1, 20),
        },
        "links": links,
    })


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


@app.get("/api/advertising")
def api_get_advertising():
    return jsonify({"ok": True, "advertising": advertising_payload()})


@app.post("/api/advertising")
def api_save_advertising():
    write_advertising(request.get_json(force=True) or {})
    return jsonify({"ok": True, "message": "广告设置已保存", "advertising": advertising_payload()})


@app.get("/api/taxonomies")
def api_taxonomies():
    return jsonify({"ok": True, **taxonomy_payload()})


@app.post("/api/taxonomies/<kind>")
def api_add_taxonomy(kind: str):
    name = validate_taxonomy(kind, (request.get_json(force=True) or {}).get("name"))
    payload = taxonomy_payload()[kind]
    if name.casefold() in {item["name"].casefold() for item in payload}:
        raise ValueError("该名称已经存在")
    ensure_taxonomy_values(kind, [name])
    if kind == "categories":
        set_category_display(name, {"show_on_home": True, "show_in_archives": True})
    label = "分类" if kind == "categories" else "标签"
    return jsonify({"ok": True, "message": f"{label}“{name}”已添加"})


@app.patch("/api/category-settings/<path:name>")
def api_category_settings(name: str):
    name = validate_taxonomy("categories", name)
    if name.casefold() not in {item["name"].casefold() for item in taxonomy_payload()["categories"]}:
        raise ValueError("分类不存在")
    set_category_display(name, request.get_json(force=True) or {})
    return jsonify({"ok": True, "message": f"分类“{name}”的显示设置已保存", "settings": category_display(name)})


@app.put("/api/taxonomies/<kind>/<path:old_name>")
def api_rename_taxonomy(kind: str, old_name: str):
    old_name = validate_taxonomy(kind, old_name)
    new_name = validate_taxonomy(kind, (request.get_json(force=True) or {}).get("name"))
    if old_name.casefold() == new_name.casefold() and old_name == new_name:
        return jsonify({"ok": True, "message": "名称没有变化"})
    existing = taxonomy_payload()[kind]
    if new_name.casefold() in {
        item["name"].casefold() for item in existing if item["name"].casefold() != old_name.casefold()
    }:
        raise ValueError("新名称已经存在")
    changed = replace_taxonomy_value(kind, old_name, new_name)
    label = "分类" if kind == "categories" else "标签"
    return jsonify({"ok": True, "message": f"{label}已重命名，同步更新 {changed} 篇文章"})


@app.delete("/api/taxonomies/<kind>/<path:name>")
def api_delete_taxonomy(kind: str, name: str):
    name = validate_taxonomy(kind, name)
    changed = replace_taxonomy_value(kind, name, None)
    label = "分类" if kind == "categories" else "标签"
    return jsonify({"ok": True, "message": f"{label}已删除，并从 {changed} 篇文章中移除"})


@app.get("/api/about")
def api_get_about():
    return jsonify({"ok": True, "about": parse_about_page()})


@app.post("/api/about")
def api_save_about():
    write_about_page(request.get_json(force=True) or {})
    return jsonify({"ok": True, "message": "关于页面已保存"})


@app.get("/api/friends")
def api_get_friends():
    return jsonify({"ok": True, "friends": friends_payload()})


@app.post("/api/friends")
def api_save_friends():
    save_friend_links(request.get_json(force=True) or {})
    return jsonify({"ok": True, "message": "友情链接已保存", "friends": friends_payload()})


@app.get("/api/posts")
def api_posts():
    return jsonify({"ok": True, "posts": all_posts()})


@app.get("/api/posts/<slug>/references")
def api_post_references(slug: str):
    path = post_path(slug)
    if not path.is_file():
        raise FileNotFoundError("文章不存在")
    return jsonify({"ok": True, "references": post_references(path.stem)})


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
    if bool(payload.get("featured", False)):
        metadata["featured"] = True
    else:
        metadata.pop("featured", None)
    if bool(payload.get("showArticleExtras", True)):
        metadata.pop("showArticleExtras", None)
    else:
        metadata["showArticleExtras"] = False
    categories = normalize_list(payload.get("categories", []))
    tags = normalize_list(payload.get("tags", []))
    ensure_taxonomy_values("categories", categories)
    ensure_taxonomy_values("tags", tags)
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
    updated_links = 0
    if original_slug and original_slug != slug:
        updated_links = update_internal_post_links(original_slug, slug)
        old_path = post_path(original_slug)
        if old_path.is_file():
            old_path.unlink()
    state = "草稿，不会显示在线" if metadata["draft"] else "公开文章"
    link_message = f"，并同步更新 {updated_links} 篇文章的内链" if updated_links else ""
    return jsonify({"ok": True, "message": f"文章已保存为{state}{link_message}", "slug": slug})


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
        raise ValueError("仅支持 PNG、JPG、WEBP、GIF 和 ICO 图片")
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


@app.post("/api/favicon")
def api_favicon():
    result = api_upload().get_json()
    settings = settings_payload()
    settings["favicon"] = result["url"]
    write_settings(settings)
    return jsonify({"ok": True, "url": result["url"], "message": "标签图标已上传并保存"})


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


@app.get("/api/github")
def api_github_connection():
    return jsonify({"ok": True, "connection": github_connection_payload()})


@app.post("/api/github")
def api_save_github_connection():
    connection = configure_github_connection(request.get_json(silent=True) or {})
    return jsonify({
        "ok": True,
        "message": f"已连接 GitHub 仓库 {connection['repository_name']}",
        "connection": connection,
    })


@app.delete("/api/github")
def api_delete_github_connection():
    path = github_settings_path()
    if path.is_file():
        path.unlink()
    return jsonify({
        "ok": True,
        "message": "本机 GitHub 连接信息已清除",
        "connection": github_connection_payload(),
    })


@app.post("/api/publish")
def api_publish():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message") or f"content: publish via TOOD Studio {datetime.now():%Y-%m-%d %H:%M}")[:180]
    try:
        git_user_name = git_text("config", "user.name")
        git_user_email = git_text("config", "user.email")
    except RuntimeError:
        git_user_name = git_user_email = ""
    if not git_user_name or not git_user_email:
        raise RuntimeError("尚未配置 Git 提交身份，请先在本页完成“连接 GitHub”设置")
    with operation_lock, tempfile.TemporaryDirectory(prefix="tood-publish-") as destination:
        build = run_command([
            tool_path("hugo"), "--source", str(BLOG_ROOT), "--destination", destination,
            "--cleanDestinationDir", "--enableGitInfo=false",
        ], timeout=180)
        managed = ["content", "data/site.toml", "data/taxonomies.toml", "static/uploads"]
        existing = [item for item in managed if (BLOG_ROOT / item).exists()]
        run_command(git_args("add", "--", *existing), timeout=30)
        staged = subprocess.run(
            git_args("diff", "--cached", "--quiet"), cwd=BLOG_ROOT, timeout=30, **process_flags()
        ).returncode
        committed = staged != 0
        if committed:
            run_command(git_args("commit", "-m", message), timeout=60)

        try:
            publish_output = push_with_github_api()
        except RuntimeError as api_error:
            logging.warning("GitHub API publish failed, trying git push: %s", api_error)
            try:
                push = run_command(git_args("push", "origin", "HEAD"), timeout=25)
                publish_output = (push.stdout + push.stderr).strip() or "Git 推送完成"
            except (RuntimeError, subprocess.TimeoutExpired) as git_error:
                raise RuntimeError(
                    f"发布失败。GitHub API：{api_error}；Git 推送：{git_error}"
                ) from git_error

    action = "内容已提交并同步" if committed else "网站已确认同步"
    return jsonify({
        "ok": True,
        "message": f"{action}到 GitHub，Cloudflare 将自动部署",
        "output": f"{publish_output}\n\n{build.stdout[-2000:]}",
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


def tray_image_path() -> Path:
    candidates = [
        Path(sys.executable).resolve().parent / "ico.png",
        Path(__file__).resolve().parent / "ico.png",
        BLOG_ROOT / "TOOD-Studio-Windows" / "ico.png",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError("未找到托盘图标 ico.png")


def create_tray_icon(url: str):
    import pystray
    from PIL import Image

    def open_dashboard(_icon=None, _item=None) -> None:
        webbrowser.open(url)

    def exit_studio(icon, _item=None) -> None:
        stop_preview()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("打开后台", open_dashboard, default=True),
        pystray.MenuItem("退出", exit_studio),
    )
    return pystray.Icon("tood-studio", Image.open(tray_image_path()), APP_NAME, menu)


def main() -> None:
    hide_windows_console()
    port = find_app_port()
    url = f"http://127.0.0.1:{port}/"
    logging.info("TOOD Studio %s started at %s for %s", APP_VERSION, url, BLOG_ROOT)
    server = threading.Thread(
        target=serve,
        kwargs={"app": app, "host": "127.0.0.1", "port": port, "threads": 6, "channel_timeout": 300},
        daemon=True,
        name="tood-studio-server",
    )
    server.start()
    if os.environ.get("TOOD_STUDIO_NO_BROWSER") != "1":
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    create_tray_icon(url).run()


if __name__ == "__main__":
    main()
