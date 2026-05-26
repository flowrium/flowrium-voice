#!/usr/bin/env python3

import argparse
import csv
import json
import os
import re
import statistics
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_MANIFESTS = [
    ROOT_DIR / "audio/standard/manifest.csv",
    ROOT_DIR / "audio/humanized/manifest.csv",
    ROOT_DIR / "audio/myvoice/manifest.csv",
]
RESULTS_DIR = ROOT_DIR / "verification-2-self" / "sensevoice" / "results"
PUNC_RE = re.compile(r'[\s，。！？；：、"\"\'\'（）()\[\]【】,.!?;:"\-]')
LABEL_RE = re.compile(r'<\|([^|]+)\|>')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch-test local audio manifests against a SenseVoice HTTP API service."
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="SenseVoice HTTP API endpoint. Default: http://localhost:8000",
    )
    parser.add_argument(
        "--manifest",
        action="append",
        dest="manifests",
        help="Manifest CSV path. Repeatable. Defaults to standard + humanized manifests.",
    )
    parser.add_argument(
        "--language",
        default="auto",
        choices=["auto", "zh", "en", "ja", "ko", "yue"],
        help="Language for SenseVoice API. Default: auto",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only test the first N rows after filtering. 0 means all rows.",
    )
    parser.add_argument(
        "--version",
        action="append",
        dest="versions",
        default=[],
        help="Only include matching version values from manifest. Repeatable.",
    )
    parser.add_argument(
        "--role",
        action="append",
        dest="roles",
        default=[],
        help="Only include matching role values from manifest. Repeatable.",
    )
    parser.add_argument(
        "--output-json",
        help="Write full test report to a JSON file.",
    )
    parser.add_argument(
        "--output-csv",
        help="Write per-file results to a CSV file.",
    )
    parser.add_argument("--output-md", help="Write Markdown summary report to a file.")
    return parser.parse_args()


def resolve_audio_path(file_path, manifest_path):
    p = Path(file_path)
    if p.is_absolute() and p.exists():
        return str(p)
    resolved = ROOT_DIR / file_path
    if resolved.exists():
        return str(resolved)
    return str(Path(manifest_path).parent / file_path)


def normalize(text):
    return PUNC_RE.sub("", text or "")


def levenshtein(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        curr = [i]
        for j, char_b in enumerate(b, start=1):
            curr.append(
                min(
                    prev[j] + 1,
                    curr[j - 1] + 1,
                    prev[j - 1] + (char_a != char_b),
                )
            )
        prev = curr
    return prev[-1]


def parse_label_result(label_result):
    if not label_result:
        return {"clean": "", "lang": None, "emotion": None}
    tags = LABEL_RE.findall(label_result)
    if not tags:
        return {"clean": label_result, "lang": None, "emotion": None}
    clean = LABEL_RE.sub("", label_result)
    # Tags order: language, emotion, event, itn flag
    lang = tags[0] if len(tags) > 0 else None
    emotion = tags[1] if len(tags) > 1 else None
    return {"clean": clean, "lang": lang, "emotion": emotion}


def load_rows(manifest_paths, versions, roles, limit):
    rows = []
    version_filter = set(versions)
    role_filter = set(roles)

    for manifest_path in manifest_paths:
        with open(manifest_path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if version_filter and row["version"] not in version_filter:
                    continue
                if role_filter and row["role"] not in role_filter:
                    continue
                row["manifest_path"] = str(manifest_path)
                row["file_path"] = resolve_audio_path(row["file_path"], row["manifest_path"])
                rows.append(row)

    if limit > 0:
        rows = rows[:limit]
    return rows


def transcribe_file(api_url, row, language):
    start_time = time.perf_counter()

    with open(row["file_path"], "rb") as f:
        files = {"file": (Path(row["file_path"]).name, f)}
        data = {"language": language}
        resp = requests.post(f"{api_url}/extract_text", files=files, data=data, timeout=120)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 1)

    if resp.status_code != 200:
        raise RuntimeError(f"API error: {resp.status_code} {resp.text[:200]}")

    result = resp.json()
    return {
        "results": result.get("results", ""),
        "label_result": result.get("label_result", ""),
        "latency_ms": latency_ms,
    }


def summarize(items):
    total = len(items)
    if total == 0:
        return {
            "count": 0,
            "passed": 0,
            "norm_exact_match_rate": 0.0,
            "cer": 0.0,
            "avg_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
        }

    norm_exact_matches = sum(1 for item in items if item["norm_exact_match"])
    expected_chars = sum(item["expected_chars"] for item in items)
    char_distance = sum(item["char_distance"] for item in items)
    latencies = sorted(item["latency_ms"] for item in items)
    p95_index = max(0, min(total - 1, int(total * 0.95) - 1))

    return {
        "count": total,
        "passed": norm_exact_matches,
        "norm_exact_match_rate": round(norm_exact_matches / total, 4),
        "cer": round(char_distance / expected_chars, 4) if expected_chars else 0.0,
        "avg_latency_ms": round(statistics.mean(latencies), 1),
        "p95_latency_ms": latencies[p95_index],
    }


def run_batch(args):
    manifest_paths = [Path(path) for path in (args.manifests or DEFAULT_MANIFESTS)]
    rows = load_rows(manifest_paths, args.versions, args.roles, args.limit)
    if not rows:
        raise SystemExit("No manifest rows matched the current filters.")

    results = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {}
        for index, row in enumerate(rows):
            future = executor.submit(transcribe_file, args.api_url, row, args.language)
            future_map[future] = (index, row)

        completed = 0
        for future in as_completed(future_map):
            completed += 1
            index, row = future_map[future]
            try:
                transcription = future.result()
            except Exception as exc:
                print(f"[{completed}/{len(rows)}] {row['id']} ERROR: {exc}", file=sys.stderr)
                continue

            parsed = parse_label_result(transcription["label_result"])
            clean_text = transcription["results"] or parsed["clean"]
            expected = row["text"]
            actual = clean_text
            expected_norm = normalize(expected)
            actual_norm = normalize(actual)
            char_distance = levenshtein(expected_norm, actual_norm)

            category = f"{row['version']}/{row['role']}"

            result = {
                "id": row["id"],
                "role": row["role"],
                "version": row["version"],
                "category": category,
                "file_path": row["file_path"],
                "manifest_path": row["manifest_path"],
                "expected": expected,
                "actual": actual,
                "expected_norm": expected_norm,
                "actual_norm": actual_norm,
                "norm_exact_match": expected_norm == actual_norm,
                "char_distance": char_distance,
                "expected_chars": len(expected_norm),
                "cer": round(char_distance / len(expected_norm), 4) if expected_norm else 0.0,
                "language_detected": parsed["lang"],
                "emotion_detected": parsed["emotion"],
                "label_result": transcription["label_result"],
                "latency_ms": transcription["latency_ms"],
            }
            results.append(result)

            lang_tag = f" lang={parsed['lang']}" if parsed["lang"] else ""
            print(
                f"[{completed}/{len(rows)}] {row['id']} "
                f"exact={result['norm_exact_match']} cer={result['cer']:.4f} "
                f"latency={result['latency_ms']}ms{lang_tag}"
            )

    by_version = defaultdict(list)
    by_role = defaultdict(list)
    by_category = defaultdict(list)
    for item in results:
        by_version[item["version"]].append(item)
        by_role[item["role"]].append(item)
        by_category[item["category"]].append(item)

    report = {
        "meta": {
            "api_url": args.api_url,
            "language": args.language,
            "manifest_paths": [str(path) for path in manifest_paths],
            "tested_count": len(results),
        },
        "summary": {
            "overall": summarize(results),
            "by_version": {key: summarize(value) for key, value in sorted(by_version.items())},
            "by_role": {key: summarize(value) for key, value in sorted(by_role.items())},
            "by_category": {key: summarize(value) for key, value in sorted(by_category.items())},
            "worst_cases": sorted(
                results, key=lambda item: (item["cer"], item["char_distance"]), reverse=True
            )[:15],
        },
        "results": results,
    }
    return report


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_markdown(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "role",
        "version",
        "category",
        "file_path",
        "expected",
        "actual",
        "norm_exact_match",
        "char_distance",
        "expected_chars",
        "cer",
        "language_detected",
        "emotion_detected",
        "latency_ms",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def fmt_pct(value):
    return f"{value:.2%}"


def fmt_ms(value):
    return f"{value:.1f}ms"


def build_markdown_report(report):
    meta = report["meta"]
    summary = report["summary"]
    overall = summary["overall"]
    manifests = ", ".join(meta["manifest_paths"])
    failed_cases = [item for item in summary["worst_cases"] if not item["norm_exact_match"]][:8]

    language_counts = defaultdict(int)
    for item in report["results"]:
        language_counts[item["language_detected"] or "unknown"] += 1

    lines = []
    lines.append("## SenseVoice Test Results")
    lines.append("")
    lines.append(
        f"**Config**: mode=offline, hotwords=no, manifests={manifests}"
    )
    lines.append("")
    lines.append("### Overall")
    lines.append("| Metric | Value | Note |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| 测试总数 (Count) | {overall['count']} | 共测试了多少条语音 |")
    lines.append(f"| 成功条数 (Passed) | {overall['passed']} | 归一化后完全匹配的条数 |")
    lines.append(
        "| **总体成功率 (Success Rate)** | "
        f"**{fmt_pct(overall['norm_exact_match_rate'])}** | 按句统计：成功条数/总条数 |"
    )
    lines.append(f"| CER (字符错误率) | {fmt_pct(overall['cer'])} | 按字统计，辅助参考 |")
    lines.append(f"| 平均最终延迟 | {fmt_ms(overall['avg_latency_ms'])} | — |")
    lines.append(f"| P95 最终延迟 | {fmt_ms(overall['p95_latency_ms'])} | — |")
    lines.append("")
    lines.append("### By Role (按角色分组的总体成功率)")
    lines.append("| Role | Count | 成功数 | **成功率** | CER |")
    lines.append("| --- | --- | --- | --- | --- |")
    for role, value in summary["by_role"].items():
        lines.append(
            f"| {role} | {value['count']} | {value['passed']} "
            f"| **{fmt_pct(value['norm_exact_match_rate'])}** | {fmt_pct(value['cer'])} |"
        )
    lines.append("")
    lines.append("### Language Detection")
    lines.append("| Language | Count |")
    lines.append("| --- | --- |")
    for language, count in sorted(language_counts.items()):
        lines.append(f"| {language} | {count} |")
    lines.append("")
    lines.append("### Failed Cases (top 8)")
    lines.append("| ID | 标记 | Expected | Actual | CER |")
    lines.append("| --- | --- | --- | --- | --- |")
    for item in failed_cases:
        lines.append(
            f"| {item['id']} | NORM_MISMATCH | {item['expected']} | {item['actual']} | {fmt_pct(item['cer'])} |"
        )
    if not failed_cases:
        lines.append("| — | — | — | — | — |")
    lines.append("")
    return "\n".join(lines)


def attach_formatted_report(report, markdown_path):
    markdown = build_markdown_report(report)
    failed_cases = [
        {**item, "marker": "NORM_MISMATCH"}
        for item in report["summary"]["worst_cases"]
        if not item["norm_exact_match"]
    ][:8]
    language_counts = defaultdict(int)
    for item in report["results"]:
        language_counts[item["language_detected"] or "unknown"] += 1

    report["report"] = {
        "format": "asr-report-format/v1",
        "engine": "SenseVoice",
        "config": {
            "mode": "offline",
            "hotwords_enabled": False,
            "manifests": report["meta"]["manifest_paths"],
            "api_url": report["meta"]["api_url"],
            "language": report["meta"]["language"],
        },
        "overall": report["summary"]["overall"],
        "by_role": [
            {"role": role, **value} for role, value in report["summary"]["by_role"].items()
        ],
        "language_detection": dict(sorted(language_counts.items())),
        "failed_cases": failed_cases,
        "markdown": markdown,
        "markdown_path": str(markdown_path),
    }
    return markdown


def print_summary(markdown):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    print()
    print(markdown)


def main():
    args = parse_args()
    try:
        report = run_batch(args)
        output_json = args.output_json or str(RESULTS_DIR / "sensevoice-results.json")
        output_csv = args.output_csv or str(RESULTS_DIR / "sensevoice-results.csv")
        output_md = args.output_md or str(RESULTS_DIR / "sensevoice-report.md")
        markdown = attach_formatted_report(report, Path(output_md))
        write_json(output_json, report)
        write_csv(output_csv, report["results"])
        write_markdown(output_md, markdown)
        print_summary(markdown)
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"Batch test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
