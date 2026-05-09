import os
import unittest
from uuid import uuid4

import requests


class NoAccidentalPublishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = os.getenv("WPC_BASE_URL", "").rstrip("/")
        if not cls.base_url:
            raise unittest.SkipTest("Set WPC_BASE_URL to run integration tests.")

        cls.user = os.getenv("WPC_USER", "")
        cls.password = os.getenv("WPC_APP_PASSWORD", "")
        cls.plugin_key = os.getenv("WPC_PLUGIN_KEY", "")

    def _headers(self, idem=True):
        h = {"Content-Type": "application/json"}
        if idem:
            h["Idempotency-Key"] = str(uuid4())
        if self.plugin_key:
            h["X-Sourov-Key"] = self.plugin_key
        return h

    def _auth(self):
        if self.user and self.password:
            return (self.user, self.password)
        return None

    def test_patch_cannot_publish_directly(self):
        create = requests.post(
            f"{self.base_url}/wp-json/sourov/v2/posts",
            json={"title": "Publish Guard Test", "content": "<p>content</p>", "status": "draft"},
            headers=self._headers(idem=True),
            auth=self._auth(),
            timeout=30,
        )
        self.assertIn(create.status_code, (200, 201), create.text)
        post_id = create.json().get("post", {}).get("id")
        self.assertTrue(post_id)

        patch = requests.patch(
            f"{self.base_url}/wp-json/sourov/v2/posts/{post_id}",
            json={"status": "publish"},
            headers=self._headers(idem=True),
            auth=self._auth(),
            timeout=30,
        )
        self.assertEqual(403, patch.status_code, patch.text)
        payload = patch.json()
        self.assertIn("error", payload)
        self.assertIn("publish", payload["error"].get("message", "").lower())


if __name__ == "__main__":
    unittest.main()
