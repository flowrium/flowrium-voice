#!/usr/bin/env python3

import argparse
import asyncio
import csv
import json
import os
import re
import statistics
import subprocess
import sys
import time
import wave
from collections import defaultdict
from pathlib import Path

import struct

import websockets


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_MANIFESTS = [
    ROOT_DIR / "audio/standard/manifest.csv",
    ROOT_DIR / "audio/humanized/manifest.csv",
    ROOT_DIR / "audio/myvoice/manifest.csv",
]
RESULTS_DIR = ROOT_DIR / "verification-2-self" / "funasr" / "results"
COMPARISON_SCRIPT = ROOT_DIR / "verification-2-self" / "scripts" / "generate_multi_engine_comparison.py"
PUNC_RE = re.compile(r'[\s，。！？；：、“”‘’（）()\[\]【】,.!?;:"\-]')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch-test local audio manifests against a FunASR WebSocket service."
    )
    parser.add_argument(
        "--ws-url",
        default="ws://127.0.0.1:10095",
        help="FunASR WebSocket endpoint. Default: ws://127.0.0.1:10095",
    )
    parser.add_argument(
        "--manifest",
        action="append",
        dest="manifests",
        help="Manifest CSV path. Repeatable. Defaults to standard + humanized manifests.",
    )
    parser.add_argument(
        "--mode",
        default="2pass",
        choices=["2pass", "online", "offline"],
        help="ASR mode sent to FunASR. Default: 2pass",
    )
    parser.add_argument(
        "--hotword",
        action="append",
        default=[],
        help="Hotword to send to FunASR. Repeatable.",
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
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run all mode x hotword combinations and generate comparison report.",
    )
    parser.add_argument(
        "--hotwords-file",
        default=str(ROOT_DIR / "config/hotwords.txt"),
        help="Hotwords file path (one word per line). Default: config/hotwords.txt",
    )
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


def build_hotwords_payload(hotwords):
    if not hotwords:
        return None
    weighted = {word: min(20 + len(word) * 25, 300) for word in hotwords}
    return json.dumps(weighted, ensure_ascii=False)


def load_hotwords_file(path):
    path = Path(path)
    if not path.exists():
        print(f"Warning: hotwords file not found: {path}", file=sys.stderr)
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def resample_16k(audio_bytes, orig_rate, sample_width, channels):
    if orig_rate == 16000:
        return audio_bytes
    frame_size = sample_width * channels
    num_frames = len(audio_bytes) // frame_size
    ratio = 16000 / orig_rate
    new_num_frames = int(num_frames * ratio)
    resampled = bytearray()
    for i in range(new_num_frames):
        src_idx = int(i / ratio)
        offset = src_idx * frame_size
        if offset + frame_size <= len(audio_bytes):
            resampled.extend(audio_bytes[offset : offset + frame_size])
    return bytes(resampled)


async def transcribe_file(ws_url, row, mode, hotwords_payload):
    config = {
        "mode": mode,
        "chunk_size": [5, 10, 5],
        "chunk_interval": 10,
        "encoder_chunk_look_back": 4,
        "decoder_chunk_look_back": 1,
        "wav_name": row["id"],
        "is_speaking": True,
        "itn": True,
    }
    if hotwords_payload:
        config["hotwords"] = hotwords_payload

    with wave.open(row["file_path"], "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        audio_bytes = wav_file.readframes(frame_count)

    if channels != 1 or sample_width != 2:
        raise RuntimeError(
            f"unsupported wav format for {row['file_path']}: "
            f"channels={channels} sample_width={sample_width}"
        )

    audio_bytes = resample_16k(audio_bytes, sample_rate, sample_width, channels)
    audio_duration_ms = round(frame_count / sample_rate * 1000, 1)

    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        await ws.send(json.dumps(config, ensure_ascii=False))

        final_text = ""
        first_partial_ms = None
        start_time = time.perf_counter()

        chunk_bytes = 15360
        for offset in range(0, len(audio_bytes), chunk_bytes):
            await ws.send(audio_bytes[offset : offset + chunk_bytes])
        await ws.send(json.dumps({"is_speaking": False}))

        async for message in ws:
            if not isinstance(message, str):
                continue
            payload = json.loads(message)
            text = payload.get("text") or ""
            if text and first_partial_ms is None:
                first_partial_ms = round((time.perf_counter() - start_time) * 1000, 1)
            if payload.get("is_final") is True or payload.get("is_final") == "true":
                final_text = text
                break

        final_latency_ms = round((time.perf_counter() - start_time) * 1000, 1)

    return {
        "final_text": final_text,
        "first_partial_ms": first_partial_ms,
        "final_latency_ms": final_latency_ms,
        "audio_ms": audio_duration_ms,
    }


def summarize(items):
    total = len(items)
    if total == 0:
        return {
            "count": 0,
            "passed": 0,
            "exact_match_rate": 0.0,
            "norm_exact_match_rate": 0.0,
            "cer": 0.0,
            "avg_final_latency_ms": 0.0,
            "p95_final_latency_ms": 0.0,
        }

    exact_matches = sum(1 for item in items if item["exact_match"])
    norm_exact_matches = sum(1 for item in items if item["norm_exact_match"])
    expected_chars = sum(item["expected_chars"] for item in items)
    char_distance = sum(item["char_distance"] for item in items)
    latencies = sorted(item["final_latency_ms"] for item in items)
    p95_index = max(0, min(total - 1, int(total * 0.95) - 1))

    return {
        "count": total,
        "passed": norm_exact_matches,
        "exact_match_rate": round(exact_matches / total, 4),
        "norm_exact_match_rate": round(norm_exact_matches / total, 4),
        "cer": round(char_distance / expected_chars, 4) if expected_chars else 0.0,
        "avg_final_latency_ms": round(statistics.mean(latencies), 1),
        "p95_final_latency_ms": latencies[p95_index],
    }


async def run_batch(args):
    manifest_paths = [Path(path) for path in (args.manifests or DEFAULT_MANIFESTS)]
    rows = load_rows(manifest_paths, args.versions, args.roles, args.limit)
    if not rows:
        raise SystemExit("No manifest rows matched the current filters.")

    hotwords_payload = build_hotwords_payload(args.hotword)
    results = []

    for index, row in enumerate(rows, start=1):
        transcription = await transcribe_file(args.ws_url, row, args.mode, hotwords_payload)
        expected = row["text"]
        actual = transcription["final_text"]
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
            "exact_match": expected == actual,
            "norm_exact_match": expected_norm == actual_norm,
            "char_distance": char_distance,
            "expected_chars": len(expected_norm),
            "cer": round(char_distance / len(expected_norm), 4) if expected_norm else 0.0,
            "audio_ms": transcription["audio_ms"],
            "first_partial_ms": transcription["first_partial_ms"],
            "final_latency_ms": transcription["final_latency_ms"],
        }
        results.append(result)
        print(
            f"[{index}/{len(rows)}] {row['id']} "
            f"exact={result['exact_match']} cer={result['cer']:.4f} "
            f"latency={result['final_latency_ms']}ms"
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
            "ws_url": args.ws_url,
            "mode": args.mode,
            "hotwords": args.hotword,
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
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_markdown(path, content):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def write_csv(path, rows):
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
        "audio_ms",
        "first_partial_ms",
        "final_latency_ms",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def _fmt_pct(val):
    return f"{val:.2%}"


def _fmt_ms(val):
    return f"{val:.1f}ms"


def build_markdown_report(report):
    meta = report["meta"]
    summary = report["summary"]
    overall = summary["overall"]
    config_hotwords = "yes" if meta["hotwords"] else "no"
    manifests = ", ".join(meta["manifest_paths"])
    failed_cases = [item for item in summary["worst_cases"] if not item["norm_exact_match"]][:8]

    lines = []
    lines.append("## FunASR Test Results")
    lines.append("")
    lines.append(
        f"**Config**: mode={meta['mode']}, hotwords={config_hotwords}, manifests={manifests}"
    )
    lines.append("")
    lines.append("### Overall")
    lines.append("| Metric | Value | Note |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| 测试总数 (Count) | {overall['count']} | 共测试了多少条语音 |")
    lines.append(f"| 成功条数 (Passed) | {overall['passed']} | 归一化后完全匹配的条数 |")
    lines.append(
        "| **总体成功率 (Success Rate)** | "
        f"**{_fmt_pct(overall['norm_exact_match_rate'])}** | 按句统计：成功条数/总条数 |"
    )
    lines.append(f"| CER (字符错误率) | {_fmt_pct(overall['cer'])} | 按字统计，辅助参考 |")
    lines.append(f"| 平均最终延迟 | {_fmt_ms(overall['avg_final_latency_ms'])} | — |")
    lines.append(f"| P95 最终延迟 | {_fmt_ms(overall['p95_final_latency_ms'])} | — |")
    lines.append("")
    lines.append("### By Role (按角色分组的总体成功率)")
    lines.append("| Role | Count | 成功数 | **成功率** | CER |")
    lines.append("| --- | --- | --- | --- | --- |")
    for role, value in summary["by_role"].items():
        lines.append(
            f"| {role} | {value['count']} | {value['passed']} "
            f"| **{_fmt_pct(value['norm_exact_match_rate'])}** | {_fmt_pct(value['cer'])} |"
        )
    lines.append("")
    lines.append("### Failed Cases (top 8)")
    lines.append("| ID | 标记 | Expected | Actual | CER |")
    lines.append("| --- | --- | --- | --- | --- |")
    for item in failed_cases:
        lines.append(
            f"| {item['id']} | NORM_MISMATCH | {item['expected']} | {item['actual']} | {_fmt_pct(item['cer'])} |"
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
    report["report"] = {
        "format": "asr-report-format/v1",
        "engine": "FunASR",
        "config": {
            "mode": report["meta"]["mode"],
            "hotwords_enabled": bool(report["meta"]["hotwords"]),
            "hotwords": report["meta"]["hotwords"],
            "manifests": report["meta"]["manifest_paths"],
            "ws_url": report["meta"]["ws_url"],
        },
        "overall": report["summary"]["overall"],
        "by_role": [
            {"role": role, **value} for role, value in report["summary"]["by_role"].items()
        ],
        "failed_cases": failed_cases,
        "markdown": markdown,
        "markdown_path": str(markdown_path),
    }
    return markdown


def print_summary(markdown):
    print()
    print(markdown)


COMPARE_MODES = ["2pass", "online", "offline"]


def _improvement_pct(before, after):
    if before == 0:
        return "N/A"
    return f"{(after - before) / before:.1%}"


def generate_report(rounds, output_path):
    lines = []
    lines.append("# Paraformer 测试报告\n")

    first_meta = rounds[0]["report"]["meta"]
    hw_round = next((r for r in rounds if r["hotwords"]), None)
    lines.append("## 测试配置\n")
    lines.append(f"- WebSocket: `{first_meta['ws_url']}`")
    lines.append(f"- 模式: {', '.join(COMPARE_MODES)}")
    lines.append(f"- 热词: {', '.join(hw_round['hotwords']) if hw_round else '(无)'}")
    lines.append(f"- 测试音频数: {first_meta['tested_count']}")
    lines.append("")

    # Collect all categories and roles across all rounds
    all_categories = set()
    all_roles = set()
    all_versions = set()
    for r in rounds:
        for item in r["report"]["results"]:
            all_categories.add(item["category"])
            all_roles.add(item["role"])
            all_versions.add(item["version"])

    # === 1. Overall summary per round ===
    lines.append("## 总览\n")
    lines.append("| 模式 | 热词 | 总数 | 通过 | 通过率 | CER |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for round_info in rounds:
        mode = round_info["mode"]
        hw = "有" if round_info["hotwords"] else "无"
        overall = round_info["report"]["summary"]["overall"]
        passed = round(int(overall["count"] * overall["norm_exact_match_rate"]))
        lines.append(
            f"| {mode} | {hw} | {overall['count']} | {passed} "
            f"| {_fmt_pct(overall['norm_exact_match_rate'])} | {_fmt_pct(overall['cer'])} |"
        )
    lines.append("")

    # === 2. Category pass rates — one big table per round ===
    lines.append("## 各分类通过率\n")
    for round_info in rounds:
        mode = round_info["mode"]
        hw = "有热词" if round_info["hotwords"] else "无热词"
        results = round_info["report"]["results"]
        by_cat = defaultdict(list)
        for r in results:
            by_cat[r["category"]].append(r)
        lines.append(f"### {mode} / {hw}\n")
        lines.append("| 分类 | 通过/总数 | 通过率 | CER |")
        lines.append("| --- | --- | --- | --- |")
        for cat in sorted(by_cat):
            cat_items = by_cat[cat]
            cat_passed = sum(1 for r in cat_items if r["norm_exact_match"])
            cat_cer = sum(r["char_distance"] for r in cat_items) / max(1, sum(r["expected_chars"] for r in cat_items))
            lines.append(
                f"| {cat} | {cat_passed}/{len(cat_items)} "
                f"| {_fmt_pct(cat_passed / len(cat_items))} | {_fmt_pct(cat_cer)} |"
            )
        lines.append("")

    # === 3. Version x Role cross table (for the primary round: 2pass + hotword) ===
    primary = next((r for r in rounds if r["mode"] == "2pass" and r["hotwords"]), None)
    if not primary:
        primary = next((r for r in rounds if r["mode"] == "2pass"), None)
    if primary:
        lines.append("## Version × Role 交叉通过率 (2pass + 热词)\n")
        primary_results = primary["report"]["results"]
        versions_sorted = sorted(all_versions)
        roles_sorted = sorted(all_roles)
        lines.append("| Version \\ Role | " + " | ".join(roles_sorted) + " |")
        lines.append("| --- | " + " | ".join(["---"] * len(roles_sorted)) + " |")
        for ver in versions_sorted:
            cells = []
            for role in roles_sorted:
                items = [r for r in primary_results if r["version"] == ver and r["role"] == role]
                if not items:
                    cells.append("-")
                else:
                    p = sum(1 for r in items if r["norm_exact_match"])
                    cells.append(f"{p}/{len(items)}")
            lines.append(f"| {ver} | " + " | ".join(cells) + " |")
        lines.append("")

    # === 4. Failed cases across all rounds ===
    lines.append("## 未通过用例\n")
    has_any_failed = False
    for round_info in rounds:
        mode = round_info["mode"]
        hw = "有热词" if round_info["hotwords"] else "无热词"
        failed = [r for r in round_info["report"]["results"] if not r["norm_exact_match"]]
        if not failed:
            continue
        has_any_failed = True
        lines.append(f"### {mode} / {hw}\n")
        lines.append("| ID | 分类 | 期望 | 实际 | CER |")
        lines.append("| --- | --- | --- | --- | --- |")
        for item in failed:
            lines.append(
                f"| {item['id']} | {item['category']} "
                f"| {item['expected']} | {item['actual']} | {_fmt_pct(item['cer'])} |"
            )
        lines.append("")
    if not has_any_failed:
        lines.append("_所有轮次全部通过_\n")

    # === 5. Mode comparison table ===
    lines.append("## 模式对比\n")
    with_hw = [r for r in rounds if r["hotwords"]]
    if with_hw:
        lines.append("| 指标 | " + " | ".join(COMPARE_MODES) + " |")
        lines.append("| --- | " + " | ".join(["---"] * len(COMPARE_MODES)) + " |")
        for metric, fmt in [
            ("cer", _fmt_pct),
            ("norm_exact_match_rate", _fmt_pct),
            ("avg_final_latency_ms", _fmt_ms),
            ("p95_final_latency_ms", _fmt_ms),
        ]:
            vals = []
            for mode in COMPARE_MODES:
                r = next((x for x in with_hw if x["mode"] == mode), None)
                vals.append(fmt(r["report"]["summary"]["overall"][metric]) if r else "N/A")
            lines.append(f"| {metric} | " + " | ".join(vals) + " |")
    else:
        lines.append("_(无热词轮次数据)_")
    lines.append("")

    # === 6. Hotword effect table ===
    lines.append("## 热词效果\n")
    no_hw = next((r for r in rounds if r["mode"] == "2pass" and not r["hotwords"]), None)
    yes_hw = next((r for r in rounds if r["mode"] == "2pass" and r["hotwords"]), None)
    if no_hw and yes_hw:
        no_s = no_hw["report"]["summary"]["overall"]
        yes_s = yes_hw["report"]["summary"]["overall"]
        lines.append("| 指标 | 无热词 | 有热词 | 提升 |")
        lines.append("| --- | --- | --- | --- |")
        for metric, fmt in [
            ("cer", _fmt_pct),
            ("norm_exact_match_rate", _fmt_pct),
            ("avg_final_latency_ms", _fmt_ms),
        ]:
            imp = _improvement_pct(no_s[metric], yes_s[metric])
            lines.append(f"| {metric} | {fmt(no_s[metric])} | {fmt(yes_s[metric])} | {imp} |")
    else:
        lines.append("_(缺少 2pass 对比数据)_")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport written to {output_path}")


def refresh_comparison_report():
    if not COMPARISON_SCRIPT.exists():
        return
    try:
        subprocess.run([sys.executable, str(COMPARISON_SCRIPT)], check=False)
    except Exception as exc:
        print(f"Warning: failed to refresh multi-engine comparison report: {exc}", file=sys.stderr)


async def run_compare(args):
    hotwords = args.hotword if args.hotword else load_hotwords_file(args.hotwords_file)

    rounds = []
    total = len(COMPARE_MODES) * 2
    round_num = 0

    for mode in COMPARE_MODES:
        for use_hotwords in [False, True]:
            round_num += 1
            hw = hotwords if use_hotwords else []
            hw_label = "hotword" if hw else "no-hotword"
            print(f"\n{'='*60}")
            print(f"[Round {round_num}/{total}] mode={mode} {hw_label}")
            print(f"{'='*60}")

            args.mode = mode
            args.hotword = hw
            try:
                report = await run_batch(args)
            except Exception as exc:
                print(f"Round {round_num} failed: {exc}", file=sys.stderr)
                continue

            suffix = f"paraformer-{mode}-{hw_label}"
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            json_path = RESULTS_DIR / f"{suffix}.json"
            write_json(json_path, report)

            rounds.append({
                "mode": mode,
                "hotwords": hw,
                "report": report,
            })

    if rounds:
        generate_report(rounds, RESULTS_DIR / "paraformer-report.md")
        refresh_comparison_report()

    return rounds


def main():
    args = parse_args()
    try:
        if args.compare:
            asyncio.run(run_compare(args))
        else:
            report = asyncio.run(run_batch(args))
            output_json = args.output_json or str(RESULTS_DIR / "paraformer-results.json")
            output_csv = args.output_csv or str(RESULTS_DIR / "paraformer-results.csv")
            output_md = args.output_md or str(RESULTS_DIR / "paraformer-single-report.md")
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            markdown = attach_formatted_report(report, Path(output_md))
            write_json(output_json, report)
            write_csv(output_csv, report["results"])
            write_markdown(output_md, markdown)
            refresh_comparison_report()
            print_summary(markdown)
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"Batch test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
