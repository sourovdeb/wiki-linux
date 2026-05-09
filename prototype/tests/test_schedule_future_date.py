import datetime as dt
import os
import unittest
from uuid import uuid4

import requests


class ScheduleValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = os.getenv("WPC_BASE_URL", "").rstrip("/")
        if not cls.base_url:
            raise unittest.SkipTest("Set WPC_BASE_URL to run integration tests.")

        cls.user = os.getenv("WPC_USER", "")
        cls.password = os.getenv("WPC_APP_PASSWORD", "")
        cls.plugin_key = os.getenv("WPC_PLUGIN_KEY", "")

    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": str(uuid4()),
        }
        if self.plugin_key:
            headers["X-Sourov-Key"] = self.plugin_key
        return headers

    def _auth(self):
        if self.user and self.password:
            return (self.user, self.password)
        return None

    def _create_draft(self):
        response = requests.post(
            f"{self.base_url}/wp-json/sourov/v2/posts",
            json={"title": "Schedule Validation", "content": "<p>body</p>", "status": "draft"},
            headers=self._headers(),
            auth=self._auth(),
            timeout=30,
        )
        self.assertIn(response.status_code, (200, 201), response.text)
        return response.json()["post"]["id"]

    def test_schedule_rejects_past_and_accepts_future(self):
        post_id = self._create_draft()

        past_iso = (dt.datetime.utcnow() - dt.timedelta(hours=2)).isoformat() + "Z"
        past = requests.post(
            f"{self.base_url}/wp-json/sourov/v2/posts/{post_id}/schedule",
            json={"date": past_iso},
            headers=self._headers(),
            auth=self._auth(),
            timeout=30,
        )
        self.assertEqual(422, past.status_code, past.text)

        future_iso = (dt.datetime.utcnow() + dt.timedelta(days=1)).isoformat() + "Z"
        future = requests.post(
            f"{self.base_url}/wp-json/sourov/v2/posts/{post_id}/schedule",
            json={"date": future_iso},
            headers=self._headers(),
            auth=self._auth(),
            timeout=30,
        )
        self.assertIn(future.status_code, (200, 201), future.text)


if __name__ == "__main__":
    unittest.main()
