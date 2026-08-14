#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${SPONSOROPS_GCP_PROJECT_ID:-}"
REGION="${SPONSOROPS_GCP_REGION:-us-central1}"
VERTEX_LOCATION="${SPONSOROPS_VERTEX_LOCATION:-global}"
MODEL="${SPONSOROPS_GEMINI_MODEL:-gemini-2.5-flash}"
SERVICE="${SPONSOROPS_SERVICE_NAME:-sponsorops}"
REPOSITORY="${SPONSOROPS_ARTIFACT_REPOSITORY:-sponsorops}"
RUNTIME_ACCOUNT="${SPONSOROPS_RUNTIME_ACCOUNT:-sponsorops-runtime}"
GCLOUD_BIN="${GCLOUD_BIN:-$(command -v gcloud || true)}"

if [[ -z "$GCLOUD_BIN" && -x /opt/homebrew/share/google-cloud-sdk/bin/gcloud ]]; then
  GCLOUD_BIN=/opt/homebrew/share/google-cloud-sdk/bin/gcloud
fi
if [[ -z "$GCLOUD_BIN" || ! -x "$GCLOUD_BIN" ]]; then
  echo "gcloud_not_found" >&2
  exit 2
fi
if [[ -z "$PROJECT_ID" ]]; then
  echo "Set SPONSOROPS_GCP_PROJECT_ID to a globally unique Google Cloud project ID." >&2
  exit 2
fi
if [[ ! "$PROJECT_ID" =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ ]]; then
  echo "invalid_google_cloud_project_id" >&2
  exit 2
fi

ACTIVE_ACCOUNT="$($GCLOUD_BIN auth list --filter=status:ACTIVE --format='value(account)' | head -n 1)"
if [[ -z "$ACTIVE_ACCOUNT" ]]; then
  echo "gcloud_authentication_required" >&2
  exit 3
fi
echo "Deploying as $ACTIVE_ACCOUNT"

if ! "$GCLOUD_BIN" projects describe "$PROJECT_ID" >/dev/null 2>&1; then
  "$GCLOUD_BIN" projects create "$PROJECT_ID" --name="SponsorOps XPRIZE" --quiet
fi
"$GCLOUD_BIN" config set project "$PROJECT_ID" --quiet

BILLING_ACCOUNT_ID="${SPONSOROPS_BILLING_ACCOUNT_ID:-}"
if [[ -z "$BILLING_ACCOUNT_ID" ]]; then
  OPEN_BILLING_ACCOUNTS=()
  while IFS= read -r account; do
    [[ -n "$account" ]] && OPEN_BILLING_ACCOUNTS+=("$account")
  done < <("$GCLOUD_BIN" billing accounts list --filter=open=true --format='value(name)' 2>/dev/null || true)
  if [[ ${#OPEN_BILLING_ACCOUNTS[@]} -eq 1 ]]; then
    BILLING_ACCOUNT_ID="${OPEN_BILLING_ACCOUNTS[0]#billingAccounts/}"
  fi
fi
if [[ -n "$BILLING_ACCOUNT_ID" ]]; then
  "$GCLOUD_BIN" billing projects link "$PROJECT_ID" \
    --billing-account="$BILLING_ACCOUNT_ID" --quiet
fi

"$GCLOUD_BIN" services enable \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com \
  run.googleapis.com \
  --project="$PROJECT_ID" --quiet

RUNTIME_EMAIL="$RUNTIME_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"
if ! "$GCLOUD_BIN" iam service-accounts describe "$RUNTIME_EMAIL" \
  --project="$PROJECT_ID" >/dev/null 2>&1; then
  "$GCLOUD_BIN" iam service-accounts create "$RUNTIME_ACCOUNT" \
    --display-name="SponsorOps Cloud Run runtime" --project="$PROJECT_ID" --quiet
fi
for role in roles/aiplatform.user roles/logging.logWriter; do
  "$GCLOUD_BIN" projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$RUNTIME_EMAIL" --role="$role" \
    --condition=None --quiet >/dev/null
done

if ! "$GCLOUD_BIN" artifacts repositories describe "$REPOSITORY" \
  --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  "$GCLOUD_BIN" artifacts repositories create "$REPOSITORY" \
    --repository-format=docker --location="$REGION" \
    --description="SponsorOps XPRIZE application images" \
    --project="$PROJECT_ID" --quiet
fi

SOURCE_REVISION="$(git rev-parse --short=12 HEAD 2>/dev/null || echo manual)"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/app:$SOURCE_REVISION"
"$GCLOUD_BIN" builds submit --config cloudbuild.yaml \
  --substitutions="_IMAGE=$IMAGE" --project="$PROJECT_ID" --quiet .

"$GCLOUD_BIN" run deploy "$SERVICE" \
  --image="$IMAGE" \
  --service-account="$RUNTIME_EMAIL" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --allow-unauthenticated \
  --cpu=1 \
  --memory=512Mi \
  --min-instances=0 \
  --max-instances=2 \
  --concurrency=20 \
  --timeout=60 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$VERTEX_LOCATION,GEMINI_MODEL=$MODEL,SPONSOROPS_HOURLY_LIMIT=30" \
  --labels="application=sponsorops,xprize=build-with-gemini" \
  --quiet

SERVICE_URL="$($GCLOUD_BIN run services describe "$SERVICE" \
  --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')"
curl -fsS "$SERVICE_URL/health" >/dev/null

RESULT_FILE="$(mktemp)"
trap 'rm -f "$RESULT_FILE"' EXIT
curl -fsS "$SERVICE_URL/api/v1/evaluate" \
  -H 'Content-Type: application/json' \
  --data @examples/opportunity.json >"$RESULT_FILE"
python3 - "$RESULT_FILE" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    result = json.load(handle)
if result.get("model") == "demo-deterministic":
    raise SystemExit("production_validation_failed_demo_model")
if result.get("decision") not in {"approve", "hold", "reject"}:
    raise SystemExit("production_validation_failed_decision")
print(json.dumps({
    "status": "production_verified",
    "decision": result["decision"],
    "model": result.get("model"),
}, sort_keys=True))
PY

echo "SponsorOps URL: $SERVICE_URL"
