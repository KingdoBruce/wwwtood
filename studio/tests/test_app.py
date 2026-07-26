import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


BLOG_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BLOG_ROOT / "studio"))
os.environ["TOOD_BLOG_ROOT"] = str(BLOG_ROOT)
os.environ["TOOD_STUDIO_NO_BROWSER"] = "1"

import app as studio  # noqa: E402


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.client = studio.app.test_client()

    def test_dashboard_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TOOD Studio", response.data)
        self.assertIn(b'input name="hero_visible"', response.data)
        self.assertIn(b'input name="hero_title_size"', response.data)
        self.assertIn(b'id="githubRepository"', response.data)
        self.assertIn(b'id="proxyHost"', response.data)
        self.assertIn(b'id="view-githubHelp"', response.data)
        self.assertIn(b'id="regenerateSlug"', response.data)
        self.assertIn(b'id="slugHint"', response.data)
        self.assertIn(b'id="quickSync"', response.data)
        self.assertIn(b'id="quickProxyEnabled"', response.data)
        self.assertNotIn(b'name="copyright_since"', response.data)

    def test_find_blog_root_accepts_myblog_child(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)
            blog = parent / "myblog"
            (blog / "config" / "_default").mkdir(parents=True)
            (blog / "config" / "_default" / "hugo.toml").write_text("", encoding="utf-8")
            (blog / "content").mkdir()
            with patch.dict(os.environ, {"TOOD_BLOG_ROOT": str(parent)}):
                self.assertEqual(studio.find_blog_root(), blog.resolve())

    def test_seo_slugify_extracts_short_core_words(self):
        self.assertEqual(studio.seo_slugify("如何优化网站 SEO"), "you-hua-wang-zhan-seo")
        self.assertEqual(
            studio.seo_slugify("2026年 Cloudflare 配置完整教程"),
            "2026-nian-cloudflare-pei-zhi",
        )
        self.assertEqual(
            studio.seo_slugify("Codex 钩子是什么，有什么用途"),
            "codex-gou-zi-yong-tu",
        )
        slug = studio.seo_slugify("这是一个非常长的中文标题用于验证自动生成结果不会超过限制并且保持完整单词")
        self.assertLessEqual(len(slug), studio.SEO_SLUG_MAX_LENGTH)
        self.assertRegex(slug, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_slug_preview_and_save_avoid_existing_post(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                posts = studio.BLOG_ROOT / "content" / "posts"
                posts.mkdir(parents=True)
                existing = posts / "you-hua-wang-zhan-seo.md"
                existing.write_text("原文章", encoding="utf-8")
                headers = {"X-TOOD-Token": studio.SESSION_TOKEN}

                preview = self.client.post(
                    "/api/posts/slug-preview",
                    json={"title": "如何优化网站 SEO"},
                    headers=headers,
                )
                self.assertEqual(preview.status_code, 200)
                self.assertEqual(preview.get_json()["slug"], "you-hua-wang-zhan-seo-2")

                existing_preview = self.client.post(
                    "/api/posts/slug-preview",
                    json={
                        "title": "如何优化网站 SEO",
                        "original_slug": "you-hua-wang-zhan-seo",
                    },
                    headers=headers,
                )
                self.assertEqual(existing_preview.get_json()["slug"], "you-hua-wang-zhan-seo")

                saved = self.client.post(
                    "/api/posts",
                    json={
                        "title": "如何优化网站 SEO",
                        "slug": "",
                        "date": "2026-07-26T12:00",
                        "draft": True,
                        "body": "正文",
                    },
                    headers=headers,
                )
                self.assertEqual(saved.status_code, 200)
                self.assertEqual(saved.get_json()["slug"], "you-hua-wang-zhan-seo-2")
                self.assertTrue((posts / "you-hua-wang-zhan-seo-2.md").is_file())

                duplicate = self.client.post(
                    "/api/posts",
                    json={
                        "title": "另一篇文章",
                        "slug": "you-hua-wang-zhan-seo",
                        "date": "2026-07-26T12:00",
                        "draft": True,
                    },
                    headers=headers,
                )
                self.assertEqual(duplicate.status_code, 400)
                self.assertIn("URL 已存在", duplicate.get_json()["error"])
                self.assertEqual(existing.read_text(encoding="utf-8"), "原文章")
            finally:
                studio.BLOG_ROOT = original_root

    def test_github_connection_configures_local_repository(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                headers = {"X-TOOD-Token": studio.SESSION_TOKEN}
                with patch.object(studio, "github_request", side_effect=[{"full_name": "owner/site"}, {"object": {"sha": "abc"}}]), patch.object(studio, "git_text", side_effect=["origin", "main"]), patch.object(studio, "run_command") as command:
                    response = self.client.post("/api/github", json={
                        "repository": "https://github.com/owner/site.git",
                        "branch": "main",
                        "user_name": "Bruce",
                        "user_email": "bruce@example.com",
                        "token": "github-token",
                    }, headers=headers)
                self.assertEqual(response.status_code, 200)
                connection = response.get_json()["connection"]
                self.assertTrue(connection["connected"])
                self.assertNotIn("token", connection)
                saved = studio.load_github_settings()
                self.assertEqual(saved["repository"], "owner/site")
                self.assertEqual(saved["token"], "github-token")
                commands = [call.args[0] for call in command.call_args_list]
                self.assertIn(studio.git_args("config", "user.name", "Bruce"), commands)
                self.assertIn(studio.git_args("config", "user.email", "bruce@example.com"), commands)
                cleared = self.client.delete("/api/github", headers=headers)
                self.assertEqual(cleared.status_code, 200)
                self.assertFalse(studio.github_settings_path().exists())
                self.assertFalse(cleared.get_json()["connection"]["connected"])
                self.assertEqual(cleared.get_json()["connection"]["repository"], "")
            finally:
                studio.BLOG_ROOT = original_root

    def test_read_apis(self):
        settings = self.client.get("/api/settings").get_json()
        advertising = self.client.get("/api/advertising").get_json()
        posts = self.client.get("/api/posts").get_json()
        github = self.client.get("/api/github").get_json()
        proxy = self.client.get("/api/proxy").get_json()
        self.assertTrue(settings["ok"])
        self.assertIn("brand_name", settings["settings"])
        self.assertIn("browser_title", settings["settings"])
        self.assertIn("favicon", settings["settings"])
        self.assertNotIn("google_ads_code", settings["settings"])
        self.assertTrue(advertising["ok"])
        self.assertIn("google_ads_code", advertising["advertising"])
        self.assertIn("home_sidebar_enabled", advertising["advertising"])
        self.assertIn("hero_visible", settings["settings"])
        self.assertIn("hero_title_size", settings["settings"])
        self.assertIn("hero_tagline_size", settings["settings"])
        self.assertTrue(posts["ok"])
        self.assertIsInstance(posts["posts"], list)
        self.assertTrue(github["ok"])
        self.assertNotIn("token", github["connection"])
        self.assertTrue(proxy["ok"])
        self.assertIn("enabled", proxy["proxy"])

    def test_proxy_settings_apply_to_github_commands(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                headers = {"X-TOOD-Token": studio.SESSION_TOKEN}
                test_result = {
                    "success": True,
                    "targets": {
                        "google": {"label": "Google", "success": True, "status": 204, "message": "连接成功（HTTP 204）"},
                        "github": {"label": "GitHub", "success": True, "status": 200, "message": "连接成功（HTTP 200）"},
                    },
                }
                with patch.object(studio, "test_proxy_connections", return_value=test_result) as test_connection:
                    response = self.client.post("/api/proxy", json={
                        "enabled": True,
                        "protocol": "http",
                        "host": "127.0.0.1",
                        "port": 7890,
                    }, headers=headers)
                self.assertEqual(response.status_code, 200)
                test_connection.assert_called_once()
                saved = studio.load_proxy_settings()
                self.assertTrue(saved["enabled"])
                self.assertEqual(studio.proxy_url(), "http://127.0.0.1:7890")
                environment = studio.command_environment()
                self.assertEqual(environment["HTTPS_PROXY"], "http://127.0.0.1:7890")
                self.assertIn("http.proxy", environment.values())
                self.assertIn("http://127.0.0.1:7890", environment.values())
            finally:
                studio.BLOG_ROOT = original_root

    def test_quick_proxy_toggle_preserves_connection_settings(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                studio.save_proxy_settings({
                    "enabled": False,
                    "protocol": "https",
                    "host": "127.0.0.1",
                    "port": 7890,
                })
                headers = {"X-TOOD-Token": studio.SESSION_TOKEN}
                enabled = self.client.patch(
                    "/api/proxy",
                    json={"enabled": True},
                    headers=headers,
                )
                self.assertEqual(enabled.status_code, 200)
                self.assertTrue(enabled.get_json()["proxy"]["enabled"])
                saved = studio.load_proxy_settings()
                self.assertEqual(saved["protocol"], "https")
                self.assertEqual(saved["host"], "127.0.0.1")
                self.assertEqual(saved["port"], 7890)

                disabled = self.client.patch(
                    "/api/proxy",
                    json={"enabled": False},
                    headers=headers,
                )
                self.assertEqual(disabled.status_code, 200)
                self.assertFalse(studio.load_proxy_settings()["enabled"])
            finally:
                studio.BLOG_ROOT = original_root

    def test_proxy_test_checks_google_and_github_when_disabled(self):
        google_response = MagicMock()
        google_response.__enter__.return_value.getcode.return_value = 204
        github_response = MagicMock()
        github_response.__enter__.return_value.getcode.return_value = 200
        opener = MagicMock()
        opener.open.side_effect = [google_response, github_response]
        with patch.object(studio.urlrequest, "build_opener", return_value=opener):
            result = studio.test_proxy_connections({
                "enabled": False,
                "protocol": "http",
                "host": "127.0.0.1",
                "port": 7890,
            })
        self.assertTrue(result["success"])
        self.assertEqual(opener.open.call_count, 2)
        urls = [call.args[0].full_url for call in opener.open.call_args_list]
        self.assertEqual(urls, [
            "https://www.google.com/generate_204",
            "https://api.github.com/",
        ])

    def test_advertising_round_trip_and_settings_preserve_ads(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                code = '<script async src="https://example.test/ads.js"></script>'
                studio.write_settings({
                    "browser_title": "TOOD.win 拾光集",
                    "favicon": "/uploads/favicon.ico",
                    "hero_visible": False,
                    "hero_title_size": 72,
                    "hero_tagline_size": 19,
                    "latest_articles_count": 8,
                    "quarter_random_count": 3,
                })
                studio.write_advertising({
                    "google_ads_code": code,
                    "home_sidebar_enabled": True,
                    "home_sidebar_code": "<ins>home</ins>",
                    "article_content_enabled": True,
                    "article_content_code": "<ins>content</ins>",
                    "article_sidebar_enabled": True,
                    "article_sidebar_code": "<ins>sidebar</ins>",
                })
                saved = studio.settings_payload()
                advertising = studio.advertising_payload()
                self.assertEqual(saved["browser_title"], "TOOD.win 拾光集")
                self.assertEqual(saved["favicon"], "/uploads/favicon.ico")
                self.assertFalse(saved["hero_visible"])
                self.assertEqual(saved["hero_title_size"], 72)
                self.assertEqual(saved["hero_tagline_size"], 19)
                self.assertEqual(saved["latest_articles_count"], 8)
                self.assertEqual(saved["quarter_random_count"], 3)
                self.assertEqual(advertising["google_ads_code"], code)
                self.assertTrue(advertising["home_sidebar_enabled"])
                self.assertEqual(advertising["article_content_code"], "<ins>content</ins>")
                studio.write_settings({"browser_title": "保留广告测试"})
                self.assertEqual(studio.advertising_payload()["article_sidebar_code"], "<ins>sidebar</ins>")
                raw = (studio.BLOG_ROOT / "data" / "site.toml").read_text(encoding="utf-8")
                self.assertIn("google_ads_code", raw)
            finally:
                studio.BLOG_ROOT = original_root

    def test_settings_hide_and_preserve_legacy_copyright_year(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                site_path = studio.BLOG_ROOT / "data" / "site.toml"
                studio.save_toml(site_path, {
                    "footer": {
                        "copyright_since": 2020,
                        "build_label": "旧页脚文字",
                    },
                })
                self.assertNotIn("copyright_since", studio.settings_payload())
                studio.write_settings({"footer_build_label": "新页脚文字"})
                footer = studio.load_toml(site_path)["footer"]
                self.assertEqual(footer["copyright_since"], 2020)
                self.assertEqual(footer["build_label"], "新页脚文字")
            finally:
                studio.BLOG_ROOT = original_root

    def test_write_requires_token(self):
        response = self.client.post("/api/markdown", json={"body": "# Test"})
        self.assertEqual(response.status_code, 403)

    def test_markdown_preview(self):
        response = self.client.post(
            "/api/markdown",
            json={"body": "# Test"},
            headers={"X-TOOD-Token": studio.SESSION_TOKEN},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<h1>Test</h1>", response.get_json()["html"])

    def test_toml_post_round_trip(self):
        content = studio.serialize_post(
            {"title": "测试", "date": "2026-07-20T12:00:00+08:00", "draft": True, "cover": "/uploads/cover.png"},
            "正文内容",
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "post.md"
            path.write_text(content, encoding="utf-8")
            metadata, body = studio.parse_post(path)
            summary = studio.post_summary(path)
        self.assertEqual(metadata["title"], "测试")
        self.assertEqual(metadata["cover"], "/uploads/cover.png")
        self.assertEqual(body.strip(), "正文内容")
        self.assertTrue(summary["showArticleExtras"])

    def test_save_post_with_cover(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                (studio.BLOG_ROOT / "content" / "posts").mkdir(parents=True)
                response = self.client.post(
                    "/api/posts",
                    json={
                        "title": "封面测试",
                        "slug": "cover-test",
                        "date": "2026-07-20T12:00",
                        "draft": False,
                        "cover": "/uploads/cover.png",
                        "featured": True,
                        "showArticleExtras": False,
                        "body": "正文",
                    },
                    headers={"X-TOOD-Token": studio.SESSION_TOKEN},
                )
                self.assertEqual(response.status_code, 200)
                metadata, _ = studio.parse_post(studio.BLOG_ROOT / "content" / "posts" / "cover-test.md")
                self.assertEqual(metadata["cover"], "/uploads/cover.png")
                self.assertTrue(metadata["featured"])
                self.assertFalse(metadata["showArticleExtras"])
                self.assertFalse(metadata["draft"])
            finally:
                studio.BLOG_ROOT = original_root

    def test_post_references_and_slug_rename_update_internal_links(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                posts = studio.BLOG_ROOT / "content" / "posts"
                posts.mkdir(parents=True)
                target = posts / "old-slug.md"
                target.write_text(
                    studio.serialize_post(
                        {"title": "目标文章", "date": "2026-07-20T12:00:00+08:00", "draft": False},
                        "目标正文",
                    ),
                    encoding="utf-8",
                )
                source = posts / "source.md"
                source.write_text(
                    studio.serialize_post(
                        {"title": "引用文章", "date": "2026-07-20T13:00:00+08:00", "draft": False},
                        "[站内链接](/posts/old-slug/)",
                    ),
                    encoding="utf-8",
                )
                references = self.client.get("/api/posts/old-slug/references")
                self.assertEqual(references.status_code, 200)
                self.assertEqual(
                    [item["slug"] for item in references.get_json()["references"]],
                    ["source"],
                )
                renamed = self.client.post(
                    "/api/posts",
                    json={
                        "original_slug": "old-slug",
                        "title": "目标文章",
                        "slug": "new-slug",
                        "date": "2026-07-20T12:00",
                        "draft": False,
                        "body": "目标正文",
                    },
                    headers={"X-TOOD-Token": studio.SESSION_TOKEN},
                )
                self.assertEqual(renamed.status_code, 200)
                self.assertFalse(target.exists())
                self.assertTrue((posts / "new-slug.md").exists())
                renamed_metadata, _ = studio.parse_post(posts / "new-slug.md")
                self.assertIn("/posts/old-slug/", renamed_metadata["aliases"])
                _, source_body = studio.parse_post(source)
                self.assertIn("](/posts/new-slug/)", source_body)
                self.assertNotIn("/posts/old-slug/", source_body)
            finally:
                studio.BLOG_ROOT = original_root

    def test_taxonomy_add_rename_and_delete_updates_posts(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                posts = studio.BLOG_ROOT / "content" / "posts"
                posts.mkdir(parents=True)
                post = posts / "taxonomy-test.md"
                post.write_text(
                    studio.serialize_post(
                        {"title": "Taxonomy", "categories": ["技术"], "tags": ["Hugo", "博客"]},
                        "Body",
                    ),
                    encoding="utf-8",
                )
                headers = {"X-TOOD-Token": studio.SESSION_TOKEN}

                added = self.client.post(
                    "/api/taxonomies/categories", json={"name": "写作"}, headers=headers
                )
                self.assertEqual(added.status_code, 200)
                renamed = self.client.put(
                    "/api/taxonomies/categories/%E6%8A%80%E6%9C%AF",
                    json={"name": "开发"},
                    headers=headers,
                )
                self.assertEqual(renamed.status_code, 200)
                deleted = self.client.delete(
                    "/api/taxonomies/tags/Hugo", headers=headers
                )
                self.assertEqual(deleted.status_code, 200)

                metadata, _ = studio.parse_post(post)
                self.assertEqual(metadata["categories"], ["开发"])
                self.assertEqual(metadata["tags"], ["博客"])
                payload = self.client.get("/api/taxonomies").get_json()
                self.assertEqual(
                    {item["name"] for item in payload["categories"]}, {"写作", "开发"}
                )
            finally:
                studio.BLOG_ROOT = original_root

    def test_about_page_edit_preserves_menu_frontmatter(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                about = studio.BLOG_ROOT / "content" / "page" / "about" / "index.zh.md"
                about.parent.mkdir(parents=True)
                about.write_text(
                    "---\ntitle: 关于\ndescription: 旧摘要\nlastmod: 2026-01-01\nmenu:\n    main:\n        weight: -90\n---\n\n旧正文\n",
                    encoding="utf-8",
                )
                response = self.client.post(
                    "/api/about",
                    json={"title": "新的关于", "description": "新摘要", "body": "## 新正文"},
                    headers={"X-TOOD-Token": studio.SESSION_TOKEN},
                )
                self.assertEqual(response.status_code, 200)
                saved = about.read_text(encoding="utf-8")
                self.assertIn("weight: -90", saved)
                self.assertIn("## 新正文", saved)
                payload = self.client.get("/api/about").get_json()["about"]
                self.assertEqual(payload["title"], "新的关于")
                self.assertEqual(payload["description"], "新摘要")
            finally:
                studio.BLOG_ROOT = original_root

    def test_friend_links_round_trip_and_validation(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                headers = {"X-TOOD-Token": studio.SESSION_TOKEN}
                response = self.client.post(
                    "/api/friends",
                    json={
                        "homepage_enabled": True,
                        "homepage_limit": 3,
                        "links": [{
                            "name": "示例网站",
                            "url": "https://example.com",
                            "description": "示例简介",
                            "logo": "/uploads/example.png",
                            "show_on_home": False,
                        }],
                    },
                    headers=headers,
                )
                self.assertEqual(response.status_code, 200)
                friends = self.client.get("/api/friends").get_json()["friends"]
                self.assertTrue(friends["homepage_enabled"])
                self.assertEqual(friends["homepage_limit"], 3)
                self.assertEqual(friends["links"][0]["name"], "示例网站")
                self.assertFalse(friends["links"][0]["show_on_home"])

                invalid = self.client.post(
                    "/api/friends",
                    json={"links": [{"name": "错误网址", "url": "javascript:alert(1)"}]},
                    headers=headers,
                )
                self.assertEqual(invalid.status_code, 400)
            finally:
                studio.BLOG_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
