from __future__ import annotations

import hmac
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import asdict

from flask import Flask, jsonify, request

from sponsorops.agent import Opportunity, build_default_agent

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(message)s")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
_agent = None
_request_times: dict[str, deque[float]] = defaultdict(deque)


def agent():
    global _agent
    if _agent is None:
        _agent = build_default_agent()
    return _agent


def authorized() -> bool:
    expected = os.environ.get("SPONSOROPS_API_KEY", "").strip()
    if not expected:
        return True
    supplied = request.headers.get("X-SponsorOps-Key", "")
    return hmac.compare_digest(expected, supplied)


def within_rate_limit() -> bool:
    identity = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    now = time.monotonic()
    bucket = _request_times[identity]
    while bucket and now - bucket[0] > 3600:
        bucket.popleft()
    if len(bucket) >= int(os.environ.get("SPONSOROPS_HOURLY_LIMIT", "30")):
        return False
    bucket.append(now)
    return True


@app.get("/")
def home():
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SponsorOps | Auditable sponsor-fit decisions</title>
<style>body{font:17px/1.55 system-ui;margin:0;background:#071b18;color:#edf8f5}main{max-width:820px;margin:auto;padding:64px 24px}.tag{color:#69d9b7;text-transform:uppercase;letter-spacing:.12em;font-weight:700}h1{font-size:clamp(2.5rem,7vw,5.5rem);line-height:.95;margin:.2em 0}code,pre{background:#102d28;border:1px solid #24554b;border-radius:8px;padding:3px 7px}section{margin-top:48px}.metric{display:inline-block;margin:8px 12px 8px 0;padding:14px 18px;background:#102d28;border-radius:12px}.metric strong{display:block;font-size:1.7rem;color:#69d9b7}a{color:#8ce6cb}</style>
</head><body><main><p class="tag">TinyOps Studio LLC</p><h1>SponsorOps</h1><p>Gemini evaluates sponsor opportunities for audience fit, evidence quality, commercial viability, and policy risk. Every decision is structured, thresholded, and written to Google Cloud logs without personal data.</p>
<div><span class="metric"><strong>$99</strong>settled arms-length revenue</span><span class="metric"><strong>1</strong>paying advertiser</span><span class="metric"><strong>$0</strong>paid acquisition spend</span></div>
<section><h2>Production decision path</h2><p>Opportunity intake → Gemini on Vertex AI → approve, hold, or reject → immutable structured log → duplicate and destination safeguards → business action.</p></section>
<section><h2>Safety by construction</h2><p>SponsorOps rejects excluded categories, downgrades low-confidence approvals, validates HTTPS destinations, caps transaction size, and never generates or sends outreach.</p></section>
<section><h2>API</h2><p><code>POST /api/v1/evaluate</code> returns an auditable decision. <code>GET /health</code> reports runtime readiness.</p></section>
</main></body></html>""", 200, {"Content-Type": "text/html; charset=utf-8"}


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "sponsorops", "gemini_configured": bool(os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("SPONSOROPS_DEMO_MODE") == "1")})


@app.post("/api/v1/evaluate")
def evaluate():
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401
    if not within_rate_limit():
        return jsonify({"error": "rate_limit_exceeded"}), 429
    if not request.is_json:
        return jsonify({"error": "application/json required"}), 415
    try:
        opportunity = Opportunity.from_mapping(request.get_json())
        decision = agent().evaluate(opportunity)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("sponsor_evaluation_failed")
        return jsonify({"error": "evaluation temporarily unavailable"}), 503
    return jsonify(asdict(decision))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))

