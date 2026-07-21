import os
import sys
import tempfile
import unittest
from pathlib import Path


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

    def test_read_apis(self):
        settings = self.client.get("/api/settings").get_json()
        posts = self.client.get("/api/posts").get_json()
        self.assertTrue(settings["ok"])
        self.assertIn("brand_name", settings["settings"])
        self.assertIn("browser_title", settings["settings"])
        self.assertIn("favicon", settings["settings"])
        self.assertIn("google_ads_code", settings["settings"])
        self.assertTrue(posts["ok"])
        self.assertIsInstance(posts["posts"], list)

    def test_google_ads_code_round_trip(self):
        original_root = studio.BLOG_ROOT
        with tempfile.TemporaryDirectory() as folder:
            try:
                studio.BLOG_ROOT = Path(folder)
                code = '<script async src="https://example.test/ads.js"></script>'
                studio.write_settings({
                    "browser_title": "TOOD.win 拾光集",
                    "favicon": "/uploads/favicon.ico",
                    "latest_articles_count": 8,
                    "quarter_random_count": 3,
                    "google_ads_code": code,
                })
                saved = studio.settings_payload()
                self.assertEqual(saved["browser_title"], "TOOD.win 拾光集")
                self.assertEqual(saved["favicon"], "/uploads/favicon.ico")
                self.assertEqual(saved["latest_articles_count"], 8)
                self.assertEqual(saved["quarter_random_count"], 3)
                self.assertEqual(saved["google_ads_code"], code)
                raw = (studio.BLOG_ROOT / "data" / "site.toml").read_text(encoding="utf-8")
                self.assertIn("google_ads_code", raw)
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
        self.assertEqual(metadata["title"], "测试")
        self.assertEqual(metadata["cover"], "/uploads/cover.png")
        self.assertEqual(body.strip(), "正文内容")

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
                        "body": "正文",
                    },
                    headers={"X-TOOD-Token": studio.SESSION_TOKEN},
                )
                self.assertEqual(response.status_code, 200)
                metadata, _ = studio.parse_post(studio.BLOG_ROOT / "content" / "posts" / "cover-test.md")
                self.assertEqual(metadata["cover"], "/uploads/cover.png")
                self.assertTrue(metadata["featured"])
                self.assertFalse(metadata["draft"])
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


if __name__ == "__main__":
    unittest.main()
