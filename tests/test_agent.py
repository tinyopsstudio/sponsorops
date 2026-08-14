import unittest

from sponsorops.agent import DemoGeminiClient, Opportunity, SponsorOpsAgent, _validated_decision


VALID = {
    "company": "Example Tackle Co",
    "website": "https://example.com/tackle",
    "offer_summary": "Durable fishing tools for freshwater anglers.",
    "audience_fit": "Direct fit for gear guides read by recreational anglers.",
    "proposed_price_usd": 149,
    "evidence": ["Public product catalog", "Working HTTPS destination"],
}


class OpportunityTests(unittest.TestCase):
    def test_valid_opportunity(self):
        opportunity = Opportunity.from_mapping(VALID)
        self.assertEqual(opportunity.proposed_price_usd, 149.0)

    def test_rejects_non_https_destination(self):
        payload = {**VALID, "website": "http://example.com"}
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            Opportunity.from_mapping(payload)

    def test_rejects_transaction_above_owner_boundary(self):
        payload = {**VALID, "proposed_price_usd": 5001}
        with self.assertRaisesRegex(ValueError, "between 0 and 5000"):
            Opportunity.from_mapping(payload)


class DecisionTests(unittest.TestCase):
    def test_demo_client_approves_relevant_opportunity(self):
        result = SponsorOpsAgent(DemoGeminiClient()).evaluate(Opportunity.from_mapping(VALID))
        self.assertEqual(result.decision, "approve")
        self.assertEqual(len(result.opportunity_hash), 16)

    def test_demo_client_rejects_excluded_category(self):
        payload = {**VALID, "offer_summary": "An online gambling promotion."}
        result = SponsorOpsAgent(DemoGeminiClient()).evaluate(Opportunity.from_mapping(payload))
        self.assertEqual(result.decision, "reject")

    def test_low_confidence_approval_fails_closed(self):
        raw = {
            "decision": "approve",
            "fit_score": 90,
            "confidence": 0.4,
            "reasons": ["Relevant offer."],
            "risks": [],
            "next_action": "Run safeguards.",
        }
        result = _validated_decision(raw, "test-model", "abc")
        self.assertEqual(result.decision, "hold")


if __name__ == "__main__":
    unittest.main()

