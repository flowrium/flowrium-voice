#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
TEST_SCRIPT="$ROOT_DIR/verification-3-edge/sherpa-onnx/scripts/test_sherpa_onnx_batch.py"

MODEL="paraformer"
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
Usage: bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh [options] [-- script args]

Options:
  --model <paraformer|sensevoice|transducer>   Model to benchmark. Default: paraformer
  --label <name>                    Output label. Default: <model>-<timestamp>
  --help                            Show this help

Any remaining arguments are passed through to test_sherpa_onnx_batch.py.

Examples:
  bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh
  bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh --model sensevoice
  bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh --model paraformer -- --version myvoice
  bash verification-3-edge/sherpa-onnx/benchmarks/apple/run_macos_benchmark.sh --model transducer -- --use-hotwords-file
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

if [[ "$MODEL" != "paraformer" && "$MODEL" != "sensevoice" && "$MODEL" != "transducer" ]]; then
  echo "Unsupported model: $MODEL" >&2
  exit 1
fi

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

echo "Running macOS benchmark:"
printf '  %q' "${RUN_CMD[@]}"
echo
echo "Log: $LOG_PATH"
echo "Time: $TIME_PATH"

(
  cd "$ROOT_DIR"
  set +e
  /usr/bin/time -l "${RUN_CMD[@]}" >"$LOG_PATH" 2>"$TIME_PATH"
  status=$?
  set -e
  if [[ $status -ne 0 ]]; then
    echo "Warning: /usr/bin/time exited with status $status; continuing with available timing output." >&2
  fi
)

RESULT_SUFFIX="no-hotword"
if [[ "$MODEL" == "transducer" ]]; then
  for arg in "${EXTRA_ARGS[@]}"; do
    if [[ "$arg" == "--hotword" || "$arg" == "--use-hotwords-file" ]]; then
      RESULT_SUFFIX="hotword"
      break
    fi
  done
fi

RESULT_JSON="$ROOT_DIR/verification-3-edge/sherpa-onnx/results/sherpa-onnx-${MODEL}-${RESULT_SUFFIX}-results.json"

python3 - "$RESULT_JSON" "$TIME_PATH" "$JSON_SUMMARY_PATH" "$MD_SUMMARY_PATH" "$MODEL" "$LABEL" "${RUN_CMD[*]}" <<'PY'
import json
import platform
import re
import subprocess
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
user_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s+user", time_text)
sys_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s+sys", time_text)

max_rss_bytes = int(rss_match.group(1)) if rss_match else None
if max_rss_bytes is not None and max_rss_bytes < 1024 * 1024:
    # macOS /usr/bin/time -l reports bytes.
    max_rss_mb = round(max_rss_bytes / 1024 / 1024, 2)
else:
    max_rss_mb = round(max_rss_bytes / 1024, 2) if max_rss_bytes is not None else None

overall = report["summary"]["overall"]
by_role = report["summary"]["by_role"]
by_version = report["summary"]["by_version"]

def safe_cmd(cmd, fallback="unknown"):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return fallback

macos_version = safe_cmd(["sw_vers", "-productVersion"])
cpu_brand = safe_cmd(["sysctl", "-n", "machdep.cpu.brand_string"], fallback=platform.processor() or "unknown")

worst_cases = [item for item in report["summary"]["worst_cases"] if not item["norm_exact_match"]][:8]

summary = {
    "label": label,
    "model": model,
    "command": command,
    "environment": {
        "platform": platform.platform(),
        "macos_version": macos_version,
        "machine": platform.machine(),
        "cpu": cpu_brand,
    },
    "performance": {
        "wall_time_s": float(secs_match.group(1)) if secs_match else None,
        "user_time_s": float(user_match.group(1)) if user_match else None,
        "sys_time_s": float(sys_match.group(1)) if sys_match else None,
        "max_rss_mb": max_rss_mb,
    },
    "accuracy": {
        "overall": overall,
        "by_role": by_role,
        "by_version": by_version,
        "worst_cases": worst_cases,
    },
    "source_result_json": str(result_json),
    "source_time_txt": str(time_txt),
}

json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

def pct(v):
    return f"{v:.2%}"

lines = []
lines.append(f"# Apple macOS Benchmark - {label}")
lines.append("")
lines.append("## Run")
lines.append("")
lines.append(f"- Command: `{command}`")
lines.append(f"- Model: `{model}`")
lines.append(f"- macOS: `{macos_version}`")
lines.append(f"- Machine: `{platform.machine()}`")
lines.append(f"- CPU: `{cpu_brand}`")
lines.append("")
lines.append("## Overall")
lines.append("")
lines.append("| Metric | Value |")
lines.append("| --- | --- |")
lines.append(f"| Count | {overall['count']} |")
lines.append(f"| Passed | {overall['passed']} |")
lines.append(f"| Success Rate | {pct(overall['norm_exact_match_rate'])} |")
lines.append(f"| CER | {pct(overall['cer'])} |")
lines.append(f"| Avg RTF | {overall['avg_rtf']:.4f} |")
lines.append(f"| P95 RTF | {overall['p95_rtf']:.4f} |")
lines.append(f"| Wall Time | {summary['performance']['wall_time_s']}s |")
lines.append(f"| Max RSS | {max_rss_mb if max_rss_mb is not None else 'n/a'} MB |")
lines.append("")
lines.append("## By Version")
lines.append("")
lines.append("| Version | Count | Passed | Success Rate | CER | Avg RTF |")
lines.append("| --- | --- | --- | --- | --- | --- |")
for version, value in sorted(by_version.items()):
    lines.append(
        f"| {version} | {value['count']} | {value['passed']} | "
        f"{pct(value['norm_exact_match_rate'])} | {pct(value['cer'])} | {value['avg_rtf']:.4f} |"
    )
lines.append("")
lines.append("## By Role")
lines.append("")
lines.append("| Role | Count | Passed | Success Rate | CER | Avg RTF |")
lines.append("| --- | --- | --- | --- | --- | --- |")
for role, value in sorted(by_role.items()):
    lines.append(
        f"| {role} | {value['count']} | {value['passed']} | "
        f"{pct(value['norm_exact_match_rate'])} | {pct(value['cer'])} | {value['avg_rtf']:.4f} |"
    )
lines.append("")
lines.append("## Worst Cases")
lines.append("")
lines.append("| ID | Expected | Actual | CER |")
lines.append("| --- | --- | --- | --- |")
for item in summary["accuracy"]["worst_cases"]:
    lines.append(
        f"| {item['id']} | {item['expected']} | {item['actual']} | {pct(item['cer'])} |"
    )
if not summary["accuracy"]["worst_cases"]:
    lines.append("| — | — | — | — |")

md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY

echo
echo "Benchmark summary written to:"
echo "  $JSON_SUMMARY_PATH"
echo "  $MD_SUMMARY_PATH"
