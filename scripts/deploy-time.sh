#!/usr/bin/env bash
# Time a Cloudflare Workers Builds deploy of one commit, from a forge.
#
# The forge's egress proxy cannot reach macron.dev itself, but Workers Builds
# reports a GitHub check run on every commit it builds, and api.github.com is
# reachable without a token (60 requests/hour). This polls that check run.
#
#   scripts/deploy-time.sh <sha> <pushed-at ISO-8601 UTC> [branch]
#
# It prints one JSON line in the public/deploys/log.jsonl format. Append it
# yourself (append-only; the file is merge=union). The poll interval is 60s
# and it gives up after 45 minutes.
set -euo pipefail
sha=${1:?sha}; pushed=${2:?pushed-at}; branch=${3:-main}
api=https://api.github.com/repos/8007342/macron.dev/commits/$sha/check-runs
for _ in $(seq 45); do
  run=$(curl -fsS -m 20 "$api" | python3 -c '
import json, sys
runs = [r for r in json.load(sys.stdin).get("check_runs", []) if r["name"].startswith("Workers Builds")]
r = runs[0] if runs else None
print(json.dumps(r and {"status": r["status"], "conclusion": r["conclusion"], "completed_at": r["completed_at"]}))
' 2>/dev/null || echo null)
  if [[ $run != null ]] && [[ $(python3 -c 'import json,sys;print(json.loads(sys.argv[1])["status"])' "$run") == completed ]]; then
    python3 - "$sha" "$pushed" "$branch" "$run" <<'PY'
import json, sys
from datetime import datetime
sha, pushed, branch, run = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
p = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
c = datetime.fromisoformat(run["completed_at"].replace("Z", "+00:00"))
print(json.dumps({"sha": sha[:7], "branch": branch, "pushed_at": pushed, "build_completed_at": run["completed_at"],
                  "seconds": int((c - p).total_seconds()), "conclusion": run["conclusion"], "measured_by": "github-check-run"}))
PY
    exit 0
  fi
  sleep 60
done
echo "gave up waiting for a Workers Builds check run on $sha" >&2; exit 1
