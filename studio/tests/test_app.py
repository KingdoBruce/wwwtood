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
        self.assertTrue(posts["ok"])
        self.assertIsInstance(posts["posts"], list)

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
                        "body": "正文",
                    },
                    headers={"X-TOOD-Token": studio.SESSION_TOKEN},
                )
                self.assertEqual(response.status_code, 200)
                metadata, _ = studio.parse_post(studio.BLOG_ROOT / "content" / "posts" / "cover-test.md")
                self.assertEqual(metadata["cover"], "/uploads/cover.png")
                self.assertFalse(metadata["draft"])
            finally:
                studio.BLOG_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
