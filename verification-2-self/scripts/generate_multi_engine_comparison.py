#!/usr/bin/env python3

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_PATH = ROOT_DIR / "verification-2-self" / "results" / "multi-engine-comparison.md"
LEGACY_OUTPUT_PATH = ROOT_DIR / "verification-2-self" / "results" / "three-engine-comparison.md"

ENGINE_SOURCES = [
    (
        "FunASR",
        [
            ROOT_DIR / "verification-2-self" / "funasr" / "results" / "paraformer-2pass-hotword.json",
            ROOT_DIR / "verification-2-self" / "funasr" / "results" / "paraformer-results.json",
        ],
        "supports hotwords and 2pass",
    ),
    (
        "SenseVoice",
        [
            ROOT_DIR / "verification-2-self" / "sensevoice" / "results" / "sensevoice-results.json",
        ],
        "offline only, no hotwords",
    ),
    (
        "WeNet",
        [
            ROOT_DIR / "verification-2-self" / "wenet" / "results" / "wenet-results.json",
        ],
        "supports hotwords and streaming",
    ),
    (
        "Qwen3-ASR",
        [
            ROOT_DIR / "verification-2-self" / "qwen3-asr" / "results" / "qwen3-asr-results.json",
        ],
        "OpenAI-compatible offline transcription API",
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


def fmt_ms(value):
    if value is None:
        return "—"
    return f"{value:.1f}ms"


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
    lines.append("## Multi-engine ASR Comparison")
    lines.append("")
    lines.append(
        "This report aggregates the latest available self-deploy results for FunASR, SenseVoice, WeNet, and Qwen3-ASR."
    )
    lines.append("")
    lines.append("### Overall")
    lines.append("| Engine | Count | Success Rate | CER | Avg Latency | P95 Latency | Notes | Source |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in available:
        overall = item["overall"]
        lines.append(
            f"| {item['engine']} | {overall.get('count', 0)} | "
            f"{fmt_pct(overall.get('norm_exact_match_rate'))} | "
            f"{fmt_pct(overall.get('cer'))} | "
            f"{fmt_ms(overall.get('avg_latency_ms') or overall.get('avg_final_latency_ms'))} | "
            f"{fmt_ms(overall.get('p95_latency_ms') or overall.get('p95_final_latency_ms'))} | "
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
        lines.append("All four engine result files are present.")
    lines.append("")
    return "\n".join(lines)


def main():
    markdown = generate_markdown()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(markdown, encoding="utf-8")
    LEGACY_OUTPUT_PATH.write_text(markdown, encoding="utf-8")
    print(f"Wrote comparison report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
