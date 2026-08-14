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


@app.after_request
def security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/")
def home():
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SponsorOps | Auditable sponsor-fit decisions</title>
<style>body{font:17px/1.55 system-ui;margin:0;background:#071b18;color:#edf8f5}main{max-width:900px;margin:auto;padding:64px 24px}.tag{color:#69d9b7;text-transform:uppercase;letter-spacing:.12em;font-weight:700}h1{font-size:clamp(2.5rem,7vw,5.5rem);line-height:.95;margin:.2em 0}code,pre{background:#102d28;border:1px solid #24554b;border-radius:8px;padding:3px 7px}section{margin-top:48px}.metric{display:inline-block;margin:8px 12px 8px 0;padding:14px 18px;background:#102d28;border-radius:12px}.metric strong{display:block;font-size:1.7rem;color:#69d9b7}a{color:#8ce6cb}.demo{display:grid;grid-template-columns:1fr 1fr;gap:14px;background:#102d28;padding:22px;border-radius:14px}label{font-size:.8rem;color:#a8cfc4}input,textarea{box-sizing:border-box;width:100%;padding:10px;margin-top:4px;border:1px solid #397467;border-radius:7px;background:#071b18;color:#edf8f5}.wide{grid-column:1/-1}.actions{display:flex;gap:10px;flex-wrap:wrap}.actions button{border:0;border-radius:999px;padding:11px 18px;background:#69d9b7;color:#071b18;font-weight:700;cursor:pointer}.actions button.secondary{background:#244e45;color:#edf8f5}#result{white-space:pre-wrap;min-height:90px;margin:0} @media(max-width:650px){.demo{grid-template-columns:1fr}.wide{grid-column:auto}}</style>
</head><body><main><p class="tag">TinyOps Studio LLC</p><h1>SponsorOps</h1><p>Gemini evaluates sponsor opportunities for audience fit, evidence quality, commercial viability, and policy risk. Every decision is structured, thresholded, and written to Google Cloud logs without personal data.</p>
<div><span class="metric"><strong>$99</strong>settled arms-length revenue</span><span class="metric"><strong>1</strong>paying advertiser</span><span class="metric"><strong>$0</strong>paid acquisition spend</span></div>
<section><h2>Production decision path</h2><p>Opportunity intake → Gemini on Vertex AI → approve, hold, or reject → immutable structured log → duplicate and destination safeguards → business action.</p></section>
<section><h2>Try a live decision</h2><form id="evaluate" class="demo">
<label>Company<input name="company" value="Example Tackle Co" maxlength="120" required></label>
<label>HTTPS website<input name="website" value="https://example.com/tackle" maxlength="500" required></label>
<label class="wide">Offer summary<textarea name="offer_summary" maxlength="1000" required>Durable fishing tools for freshwater anglers.</textarea></label>
<label class="wide">Audience fit<textarea name="audience_fit" maxlength="1000" required>Direct fit for gear guides read by recreational anglers.</textarea></label>
<label>Proposed price, USD<input name="proposed_price_usd" type="number" min="0" max="5000" step="0.01" value="149" required></label>
<label>Evidence, one item per line<textarea name="evidence" maxlength="1200">Public product catalog\nWorking HTTPS destination</textarea></label>
<div class="wide actions"><button type="submit">Evaluate with Gemini</button><button class="secondary" id="safe" type="button">Load outdoor example</button><button class="secondary" id="reject" type="button">Load rejected example</button></div>
</form><pre id="result">Decision output will appear here.</pre></section>
<section><h2>Safety by construction</h2><p>SponsorOps rejects excluded categories, downgrades low-confidence approvals, validates HTTPS destinations, caps transaction size, and never generates or sends outreach.</p></section>
<section><h2>API</h2><p><code>POST /api/v1/evaluate</code> returns an auditable decision. <code>GET /health</code> reports runtime readiness.</p></section>
<script>const form=document.querySelector('#evaluate'),out=document.querySelector('#result');const set=(unsafe=false)=>{form.company.value=unsafe?'FastWin Casino':'Example Tackle Co';form.website.value=unsafe?'https://example.com/casino':'https://example.com/tackle';form.offer_summary.value=unsafe?'Online gambling promotion for cash prizes.':'Durable fishing tools for freshwater anglers.';form.audience_fit.value=unsafe?'Requests placement despite weak audience relevance.':'Direct fit for gear guides read by recreational anglers.';form.proposed_price_usd.value=unsafe?'499':'149';form.evidence.value=unsafe?'Promotional landing page':'Public product catalog\\nWorking HTTPS destination';out.textContent='Example loaded. Select Evaluate with Gemini.'};document.querySelector('#safe').onclick=()=>set(false);document.querySelector('#reject').onclick=()=>set(true);form.onsubmit=async(e)=>{e.preventDefault();out.textContent='Gemini is evaluating the opportunity...';const f=new FormData(form),payload=Object.fromEntries(f.entries());payload.proposed_price_usd=Number(payload.proposed_price_usd);payload.evidence=payload.evidence.split('\\n').map(x=>x.trim()).filter(Boolean);try{const r=await fetch('/api/v1/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}),data=await r.json();out.textContent=JSON.stringify(data,null,2)}catch(err){out.textContent='Evaluation temporarily unavailable.'}};</script>
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
