#!/usr/bin/env python3

import csv
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path


PUNC_RE = re.compile(r'[\s，。！？；：、“”‘’（）()\[\]【】,.!?;:"\-]')


def default_manifests(root_dir):
    return [
        root_dir / "audio/standard/manifest.csv",
        root_dir / "audio/humanized/manifest.csv",
        root_dir / "audio/myvoice/manifest.csv",
    ]


def resolve_audio_path(root_dir, file_path, manifest_path):
    path = Path(file_path)
    if path.is_absolute() and path.exists():
        return str(path)
    resolved = root_dir / file_path
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


def load_rows(root_dir, manifest_paths, versions, roles, limit):
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
                row["file_path"] = resolve_audio_path(root_dir, row["file_path"], row["manifest_path"])
                row["category"] = f"{row['version']}/{row['role']}"
                rows.append(row)

    if limit > 0:
        rows = rows[:limit]
    return rows


def summarize(items, perf_key):
    total = len(items)
    if total == 0:
        return {
            "count": 0,
            "passed": 0,
            "norm_exact_match_rate": 0.0,
            "cer": 0.0,
            f"avg_{perf_key}": 0.0,
            f"p95_{perf_key}": 0.0,
        }

    norm_exact_matches = sum(1 for item in items if item["norm_exact_match"])
    expected_chars = sum(item["expected_chars"] for item in items)
    char_distance = sum(item["char_distance"] for item in items)
    perf_values = sorted(item[perf_key] for item in items)
    p95_index = max(0, min(total - 1, int(total * 0.95) - 1))

    return {
        "count": total,
        "passed": norm_exact_matches,
        "norm_exact_match_rate": round(norm_exact_matches / total, 4),
        "cer": round(char_distance / expected_chars, 4) if expected_chars else 0.0,
        f"avg_{perf_key}": round(statistics.mean(perf_values), 4),
        f"p95_{perf_key}": perf_values[p95_index],
    }


def build_report(meta, results, perf_key):
    by_version = defaultdict(list)
    by_role = defaultdict(list)
    by_category = defaultdict(list)
    for item in results:
        by_version[item["version"]].append(item)
        by_role[item["role"]].append(item)
        by_category[item["category"]].append(item)

    return {
        "meta": meta,
        "summary": {
            "overall": summarize(results, perf_key),
            "by_version": {key: summarize(value, perf_key) for key, value in sorted(by_version.items())},
            "by_role": {key: summarize(value, perf_key) for key, value in sorted(by_role.items())},
            "by_category": {key: summarize(value, perf_key) for key, value in sorted(by_category.items())},
            "worst_cases": sorted(
                results, key=lambda item: (item["cer"], item["char_distance"]), reverse=True
            )[:15],
        },
        "results": results,
    }


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_csv(path, rows, extra_fieldnames=None):
    fieldnames = [
        "id",
        "role",
        "version",
        "category",
        "file_path",
        "expected",
        "actual",
        "exact_match",
        "norm_exact_match",
        "char_distance",
        "expected_chars",
        "cer",
        "rtf",
        "audio_duration_s",
        "inference_time_s",
    ]
    if extra_fieldnames:
        fieldnames.extend(extra_fieldnames)

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def fmt_pct(value):
    return f"{value:.2%}"


def build_markdown_report(report, engine_title, config_line, perf_key="rtf", perf_label="RTF"):
    summary = report["summary"]
    overall = summary["overall"]
    failed_cases = [item for item in summary["worst_cases"] if not item["norm_exact_match"]][:8]

    lines = []
    lines.append(f"## {engine_title} Test Results")
    lines.append("")
    lines.append(f"**Config**: {config_line}")
    lines.append("")
    lines.append("### Overall")
    lines.append("| Metric | Value | Note |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| 测试总数 | {overall['count']} | |")
    lines.append(f"| 成功条数 | {overall['passed']} | 归一化后完全匹配 |")
    lines.append(f"| **成功率** | **{fmt_pct(overall['norm_exact_match_rate'])}** | 成功条数/总条数 |")
    lines.append(f"| CER | {fmt_pct(overall['cer'])} | 字符错误率 |")
    lines.append(f"| 平均 {perf_label} | {overall[f'avg_{perf_key}']:.4f} | <1.0 表示快于实时 |")
    lines.append(f"| P95 {perf_label} | {overall[f'p95_{perf_key}']:.4f} | |")
    lines.append("")
    lines.append("### By Role")
    lines.append("| Role | Count | 成功数 | **成功率** | CER | Avg RTF |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for role, value in summary["by_role"].items():
        lines.append(
            f"| {role} | {value['count']} | {value['passed']} "
            f"| **{fmt_pct(value['norm_exact_match_rate'])}** "
            f"| {fmt_pct(value['cer'])} | {value[f'avg_{perf_key}']:.4f} |"
        )
    lines.append("")
    lines.append("### By Version")
    lines.append("| Version | Count | 成功数 | **成功率** | CER | Avg RTF |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for version, value in summary["by_version"].items():
        lines.append(
            f"| {version} | {value['count']} | {value['passed']} "
            f"| **{fmt_pct(value['norm_exact_match_rate'])}** "
            f"| {fmt_pct(value['cer'])} | {value[f'avg_{perf_key}']:.4f} |"
        )
    lines.append("")
    lines.append("### Failed Cases (top 8)")
    lines.append("| ID | Expected | Actual | CER |")
    lines.append("| --- | --- | --- | --- |")
    for item in failed_cases:
        lines.append(
            f"| {item['id']} | {item['expected']} | {item['actual']} | {fmt_pct(item['cer'])} |"
        )
    if not failed_cases:
        lines.append("| — | — | — | — |")
    lines.append("")
    return "\n".join(lines)


def write_result_bundle(
    results_dir,
    prefix,
    report,
    engine_title,
    config_line,
    extra_fieldnames=None,
):
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = results_dir / f"{prefix}-results.json"
    csv_path = results_dir / f"{prefix}-results.csv"
    md_path = results_dir / f"{prefix}-report.md"
    markdown = build_markdown_report(report, engine_title=engine_title, config_line=config_line)
    write_json(json_path, report)
    write_csv(csv_path, report["results"], extra_fieldnames=extra_fieldnames)
    md_path.write_text(markdown, encoding="utf-8")
    return json_path, csv_path, md_path, markdown
