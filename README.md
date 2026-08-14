# SponsorOps

SponsorOps is an auditable Gemini decision agent for independent publishers that need to turn relevant sponsor opportunities into revenue without hiring a sales-operations team.

The business workflow was created by TinyOps Studio LLC in July 2026, within the Build with Gemini XPRIZE submission period. Its first deployment operates Troutmate, a small fishing publisher. It produced one new arms-length advertiser customer and $99 in settled sponsored-content revenue on July 23, 2026 with $0 in paid customer-acquisition spend.

## What Gemini does in production

Each sponsor opportunity is sent to Gemini on Vertex AI. Gemini evaluates audience fit, evidence quality, commercial viability, and policy risk, then returns one structured decision:

- `approve`: relevant and sufficiently supported
- `hold`: material facts or confidence need review
- `reject`: excluded, unsafe, unsupported, or irrelevant

The service validates inputs, downgrades low-confidence approvals, and writes a PII-free structured decision event to Google Cloud Logging. Contact, duplicate, and destination safeguards still run before any business message. SponsorOps does not generate or send outreach.

## Architecture

```text
Opportunity intake
      |
      v
Cloud Run API --> Gemini on Vertex AI --> threshold and policy checks
      |                                      |
      +---------------- Cloud Logging <------+
                             |
                             v
                   approve / hold / reject
```

Google Cloud products used: Cloud Run, Vertex AI, Cloud Build, Artifact Registry, and Cloud Logging.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
SPONSOROPS_DEMO_MODE=1 python app.py
```

The deterministic demo mode exists only for local tests. Production defaults to Vertex AI and fails closed if `GOOGLE_CLOUD_PROJECT` is absent.

```bash
curl -sS http://localhost:8080/api/v1/evaluate \
  -H 'Content-Type: application/json' \
  --data @examples/opportunity.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Deploy to Google Cloud Run

```bash
export SPONSOROPS_GCP_PROJECT_ID=tinyops-sponsorops-2026
./ops/deploy_gcp.sh
```

The deployment script creates or reuses the project, attaches the only open billing account when one is available, enables the required APIs, creates a least-privilege runtime service account, builds the revision in Cloud Build, deploys it to Cloud Run, and makes one production Gemini decision. It stops if the result reports the deterministic demo model. Set `SPONSOROPS_BILLING_ACCOUNT_ID` when the Google account has more than one open billing account.

The runtime service account receives `roles/aiplatform.user` and `roles/logging.logWriter`. Set `SPONSOROPS_API_KEY` for restricted judging access and lower `SPONSOROPS_HOURLY_LIMIT` if needed.

## Newness and pre-existing work

SponsorOps is a new business workflow created after May 19, 2026. It uses an existing TinyOps Studio LLC legal entity and a pre-existing acquired publishing asset, which the XPRIZE FAQ permits. Generic automation, website, email, finance-ledger, and marketplace utilities existed before SponsorOps. The sponsor-fit policy, opportunity controller, revenue workflow, Gemini decision service, business offer, and operating evidence were created during the submission period.

The acquired Troutmate asset and any expenses incurred before May 19 are disclosed separately and are excluded from the hackathon-period SponsorOps P&L.

## Safety and privacy

- no customer contact details in logs or source
- HTTPS-only advertiser destinations
- excluded-category rejection policy
- maximum transaction value of $5,000 at intake
- low-confidence approvals automatically become `hold`
- generic error messages, body-size cap, API-key option, and hourly rate limit
- real customer evidence is anonymized unless the customer consents to disclosure

## License

MIT, copyright 2026 TinyOps Studio LLC.
