# SponsorOps demo video script

Target runtime: 2 minutes 40 seconds

## 0:00 to 0:18, problem and proof

Visual: SponsorOps home page, title and three business metrics.

Narration:

Independent publishers have valuable audiences, but sponsor operations can cost more than the first sale. SponsorOps is a new AI-operated sponsorship desk created by TinyOps Studio during the XPRIZE period. Its first deployment produced one arms-length advertiser customer, $99 in settled revenue, and zero paid customer-acquisition spend.

## 0:18 to 0:40, operating model

Visual: production decision path on the home page, then a simple architecture card.

Narration:

The workflow begins with an advertiser opportunity. Gemini on Vertex AI decides whether it should be approved, held, or rejected. Explicit safeguards then check duplicates, destination safety, evidence, consent, and price before any business action. Every decision is written to Google Cloud Logging without personal data.

## 0:40 to 1:15, live approval

Visual: load the outdoor example, review the inputs, select Evaluate with Gemini, and show the structured approval.

Narration:

Here is a live opportunity for fishing tools. The input contains the company, HTTPS destination, offer, audience fit, proposed price, and evidence. Gemini returns a structured approval with a fit score, confidence, reasons, risks, and a bounded next action. Low-confidence approvals are automatically downgraded to hold.

## 1:15 to 1:43, live rejection

Visual: load the rejected example, evaluate it, and show the rejection.

Narration:

Now the same production endpoint receives an excluded gambling offer. Gemini rejects it, explains the policy risk, and tells the operator to suppress the opportunity. SponsorOps never generates or sends outreach, and untrusted fields are treated as data instead of instructions.

## 1:43 to 2:05, Google Cloud evidence

Visual: Cloud Run service metrics, Vertex AI model observability, and a redacted Cloud Logging decision event.

Narration:

The service runs on Cloud Run and calls Gemini through Vertex AI. These Cloud Run metrics, Vertex AI observability, and structured decision logs show that the agent is executing in production. Cloud Build and Artifact Registry provide the repeatable deployment path.

## 2:05 to 2:28, real business evidence

Visual: privacy-safe sponsor fulfillment case study, redacted settled payment, and monthly P&L.

Narration:

The first engagement was a new, unrelated advertiser. SponsorOps supported the offer, review, payment reconciliation, fulfillment, and audit evidence. Revenue was $99 in July. Related-party revenue and paid marketing spend were both zero. Customer contact data is anonymized because consent to share it was not requested.

## 2:28 to 2:40, impact and close

Visual: mobile SponsorOps page and repository URL.

Narration:

SponsorOps gives small publishers an auditable path from audience to sponsor revenue, with a success-fee or monthly operating model. The live service and source are ready for testing.

## Required final QA

- total video duration is under 3 minutes
- English captions are included
- every production claim shown is verified after live deployment
- no owner name, customer contact information, bank data, secrets, or private URLs appear
- no third-party music, trademarks, or copyrighted footage appear
- public video description links to the live service and public repository

