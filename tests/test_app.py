import os
import unittest

os.environ["SPONSOROPS_DEMO_MODE"] = "1"

from app import app


VALID = {
    "company": "Example Tackle Co",
    "website": "https://example.com/tackle",
    "offer_summary": "Durable fishing tools for freshwater anglers.",
    "audience_fit": "Direct fit for gear guides read by recreational anglers.",
    "proposed_price_usd": 149,
    "evidence": ["Public product catalog"],
}


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_evaluate(self):
        response = self.client.post("/api/v1/evaluate", json=VALID)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["decision"], "approve")

    def test_validation_error(self):
        response = self.client.post("/api/v1/evaluate", json={**VALID, "website": "javascript:alert(1)"})
        self.assertEqual(response.status_code, 400)

    def test_home_includes_live_decision_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Evaluate with Gemini", response.data)


if __name__ == "__main__":
    unittest.main()
