#!/usr/bin/env python3

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_PATH = ROOT_DIR / "verification-3-edge" / "results" / "multi-engine-comparison.md"

ENGINE_SOURCES = [
    (
        "Sherpa-ONNX",
        [
            ROOT_DIR / "verification-3-edge" / "sherpa-onnx" / "results" / "sherpa-onnx-paraformer-no-hotword-results.json",
            ROOT_DIR / "verification-3-edge" / "sherpa-onnx" / "results" / "sherpa-onnx-sensevoice-no-hotword-results.json",
        ],
        "native ONNX edge runtime",
    ),
    (
        "whisper.cpp",
        [
            ROOT_DIR / "verification-3-edge" / "whisper.cpp" / "results" / "whisper-cpp-base-no-hotword-results.json",
        ],
        "GGML/GGUF local inference",
    ),
    (
        "Moonshine",
        [
            ROOT_DIR / "verification-3-edge" / "moonshine" / "results" / "moonshine-mandarin-no-hotword-results.json",
        ],
        "Useful Sensors local model",
    ),
    (
        "WeNet Runtime",
        [
            ROOT_DIR / "verification-3-edge" / "wenet-runtime" / "results" / "wenet-runtime-docker-bundled-no-hotword-results.json",
            ROOT_DIR / "verification-3-edge" / "wenet-runtime" / "results" / "wenet-runtime-docker-bundled-hotword-results.json",
        ],
        "runtime server over WebSocket",
    ),
]


def load_engine_report(paths):
    for path in paths:
        if path.exists():
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
            return path, payload
    return None, None


def fmt_pct(value):
    if value is None:
        return "—"
    return f"{value:.2%}"


def generate_markdown():
    available = []
    missing = []
    category_union = set()

    for engine_name, candidates, note in ENGINE_SOURCES:
        path, payload = load_engine_report(candidates)
        if not payload:
            missing.append(engine_name)
            continue
        summary = payload.get("summary", {})
        overall = summary.get("overall", {})
        by_category = summary.get("by_category", {})
        category_union.update(by_category.keys())
        available.append(
            {
                "engine": engine_name,
                "path": path,
                "note": note,
                "overall": overall,
                "by_category": by_category,
            }
        )

    lines = []
    lines.append("## Edge Multi-engine ASR Comparison")
    lines.append("")
    lines.append("This report aggregates the latest available edge verification results.")
    lines.append("")
    lines.append("### Overall")
    lines.append("| Engine | Count | Success Rate | CER | Avg RTF | P95 RTF | Notes | Source |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in available:
        overall = item["overall"]
        lines.append(
            f"| {item['engine']} | {overall.get('count', 0)} | "
            f"{fmt_pct(overall.get('norm_exact_match_rate'))} | "
            f"{fmt_pct(overall.get('cer'))} | "
            f"{overall.get('avg_rtf', '—')} | "
            f"{overall.get('p95_rtf', '—')} | "
            f"{item['note']} | {item['path'].relative_to(ROOT_DIR)} |"
        )
    if not available:
        lines.append("| — | — | — | — | — | — | — | — |")
    lines.append("")
    lines.append("### By Category")
    lines.append("| Category | Engine | Success Rate | CER |")
    lines.append("| --- | --- | --- | --- |")
    if category_union:
        for category in sorted(category_union):
            for item in available:
                stats = item["by_category"].get(category)
                if not stats:
                    lines.append(f"| {category} | {item['engine']} | — | — |")
                    continue
                lines.append(
                    f"| {category} | {item['engine']} | "
                    f"{fmt_pct(stats.get('norm_exact_match_rate'))} | "
                    f"{fmt_pct(stats.get('cer'))} |"
                )
    else:
        lines.append("| — | — | — | — |")
    lines.append("")
    lines.append("### Availability")
    if missing:
        lines.append(f"Missing result files for: {', '.join(missing)}")
    else:
        lines.append("All configured edge result files are present.")
    lines.append("")
    return "\n".join(lines)


def main():
    markdown = generate_markdown()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(markdown, encoding="utf-8")
    print(f"Wrote comparison report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
