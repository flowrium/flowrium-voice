#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
TEST_SCRIPT="$ROOT_DIR/verification-3-edge/moonshine/scripts/test_moonshine_batch.py"

MODEL="mandarin"
LABEL=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    --label)
      LABEL="$2"
      shift 2
      ;;
    --help|-h)
      cat <<'EOF'
Usage: bash verification-3-edge/moonshine/benchmarks/apple/run_macos_benchmark.sh [options] [-- script args]
EOF
      exit 0
      ;;
    --)
      shift
      EXTRA_ARGS+=("$@")
      break
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

mkdir -p "$RESULTS_DIR"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
if [[ -z "$LABEL" ]]; then
  LABEL="${MODEL}-${TIMESTAMP}"
fi

LOG_PATH="$RESULTS_DIR/${LABEL}.log"
TIME_PATH="$RESULTS_DIR/${LABEL}.time.txt"
JSON_SUMMARY_PATH="$RESULTS_DIR/${LABEL}-benchmark.json"
MD_SUMMARY_PATH="$RESULTS_DIR/${LABEL}-benchmark.md"

RUN_CMD=(python3 "$TEST_SCRIPT" --model "$MODEL")
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
  RUN_CMD+=("${EXTRA_ARGS[@]}")
fi

(
  cd "$ROOT_DIR"
  /usr/bin/time -l "${RUN_CMD[@]}" >"$LOG_PATH" 2>"$TIME_PATH"
)

RESULT_JSON="$ROOT_DIR/verification-3-edge/moonshine/results/moonshine-${MODEL}-no-hotword-results.json"

python3 - "$RESULT_JSON" "$TIME_PATH" "$JSON_SUMMARY_PATH" "$MD_SUMMARY_PATH" "$MODEL" "$LABEL" "${RUN_CMD[*]}" <<'PY'
import json
import re
import sys
from pathlib import Path

result_json = Path(sys.argv[1])
time_txt = Path(sys.argv[2])
json_out = Path(sys.argv[3])
md_out = Path(sys.argv[4])
model = sys.argv[5]
label = sys.argv[6]
command = sys.argv[7]

report = json.load(result_json.open(encoding="utf-8"))
time_text = time_txt.read_text(encoding="utf-8", errors="replace")
rss_match = re.search(r"maximum resident set size\s+(\d+)", time_text)
secs_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s+real", time_text)
max_rss_bytes = int(rss_match.group(1)) if rss_match else None
max_rss_mb = round(max_rss_bytes / 1024 / 1024, 2) if max_rss_bytes is not None else None
overall = report["summary"]["overall"]

summary = {
    "label": label,
    "model": model,
    "command": command,
    "performance": {
        "wall_time_s": float(secs_match.group(1)) if secs_match else None,
        "max_rss_mb": max_rss_mb,
    },
    "accuracy": overall,
}
json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
md_out.write_text(
    "\n".join(
        [
            f"# Apple macOS Benchmark - {label}",
            "",
            f"- Command: `{command}`",
            f"- Model: `{model}`",
            f"- Success Rate: `{overall['norm_exact_match_rate']:.2%}`",
            f"- CER: `{overall['cer']:.2%}`",
            f"- Avg RTF: `{overall['avg_rtf']:.4f}`",
            f"- P95 RTF: `{overall['p95_rtf']:.4f}`",
            f"- Wall Time: `{summary['performance']['wall_time_s']}`",
            f"- Max RSS MB: `{max_rss_mb}`",
            "",
        ]
    ),
    encoding="utf-8",
)
PY
