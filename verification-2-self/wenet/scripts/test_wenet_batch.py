#!/usr/bin/env python3

import argparse
import asyncio
import csv
import json
import re
import statistics
import sys
import time
import wave
from collections import defaultdict
from pathlib import Path

import websockets


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_MANIFESTS = [
    ROOT_DIR / "audio/standard/manifest.csv",
    ROOT_DIR / "audio/humanized/manifest.csv",
    ROOT_DIR / "audio/myvoice/manifest.csv",
]
RESULTS_DIR = ROOT_DIR / "verification-2-self" / "wenet" / "results"
PUNC_RE = re.compile(r'[\s，。！？；：、“”‘’（）()\[\]【】,.!?;:"\-]')
CATEGORY_PREFIX_RE = re.compile(r"^[A-F]-")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch-test local audio manifests against a WeNet WebSocket service."
    )
    parser.add_argument(
        "--ws-url",
        default="ws://127.0.0.1:10097",
        help="WeNet WebSocket endpoint. Default: ws://127.0.0.1:10097",
    )
    parser.add_argument(
        "--manifest",
        action="append",
        dest="manifests",
        help="Manifest CSV path. Repeatable. Defaults to standard + humanized + myvoice manifests.",
    )
    parser.add_argument(
        "--hotword",
        action="append",
        default=[],
        help="Hotword to send to WeNet. Repeatable.",
    )
    parser.add_argument(
        "--hotwords-file",
        help="Hotwords file path (one word per line).",
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
    parser.add_argument("--output-json", help="Write full test report to a JSON file.")
    parser.add_argument("--output-csv", help="Write per-file results to a CSV file.")
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


def infer_category(file_path):
    path = Path(file_path)
    for part in path.parts:
        if CATEGORY_PREFIX_RE.match(part):
            return part
    return "tts-baseline"


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


def load_hotwords_file(path):
    hotwords_path = Path(path)
    if not hotwords_path.exists():
        print(f"Warning: hotwords file not found: {hotwords_path}", file=sys.stderr)
        return []
    with open(hotwords_path, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


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


def chunk_audio(audio_bytes, frame_samples=960, sample_width=2):
    chunk_bytes = frame_samples * sample_width
    for offset in range(0, len(audio_bytes), chunk_bytes):
        yield audio_bytes[offset : offset + chunk_bytes]


def build_start_signal(row_id, hotwords):
    signal = {"signal": "start", "nbest": 1, "wav_name": row_id}
    if hotwords:
        signal["hotwords"] = hotwords
    return signal


def parse_sentence(payload):
    nbest = payload.get("nbest") or []
    if isinstance(nbest, str):
        try:
            nbest = json.loads(nbest)
        except json.JSONDecodeError:
            return nbest.strip()
    if not nbest:
        return ""
    first = nbest[0] or {}
    if isinstance(first, str):
        return first.strip()
    return (first.get("sentence") or first.get("text") or "").strip()


async def transcribe_file(ws_url, row, hotwords):
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
        await ws.send(json.dumps(build_start_signal(row["id"], hotwords), ensure_ascii=False))

        final_text = ""
        first_partial_ms = None
        start_time = time.perf_counter()

        for chunk in chunk_audio(audio_bytes):
            await ws.send(chunk)

        await ws.send(json.dumps({"signal": "end"}))

        async for message in ws:
            if not isinstance(message, str):
                continue
            payload = json.loads(message)
            text = parse_sentence(payload)
            if text and first_partial_ms is None:
                first_partial_ms = round((time.perf_counter() - start_time) * 1000, 1)

            status = payload.get("status")
            signal = payload.get("signal")
            typ = payload.get("type")
            is_final = (
                signal == "end"
                or typ == "final_result"
                or payload.get("is_final") is True
                or payload.get("final") is True
            )
            if text:
                final_text = text
            if is_final or status == "done":
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

    hotwords = list(args.hotword)
    if args.hotwords_file:
        hotwords = load_hotwords_file(args.hotwords_file)

    results = []
    for index, row in enumerate(rows, start=1):
        try:
            transcription = await transcribe_file(args.ws_url, row, hotwords)
        except Exception as exc:
            print(f"[{index}/{len(rows)}] {row['id']} ERROR: {exc}", file=sys.stderr)
            continue

        expected = row["text"]
        actual = transcription["final_text"]
        expected_norm = normalize(expected)
        actual_norm = normalize(actual)
        char_distance = levenshtein(expected_norm, actual_norm)
        category = infer_category(row["file_path"])

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

    return {
        "meta": {
            "ws_url": args.ws_url,
            "hotwords": hotwords,
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


def fmt_pct(value):
    return f"{value:.2%}"


def fmt_ms(value):
    return f"{value:.1f}ms"


def build_markdown_report(report):
    meta = report["meta"]
    summary = report["summary"]
    overall = summary["overall"]
    hotwords = meta["hotwords"]
    config_hotwords = "yes" if hotwords else "no"
    manifests = ", ".join(meta["manifest_paths"])

    lines = []
    lines.append("## WeNet Test Results")
    lines.append("")
    lines.append(
        f"**Config**: mode=single, hotwords={config_hotwords}, manifests={manifests}"
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
    lines.append(
        f"| 平均最终延迟 | {fmt_ms(overall['avg_final_latency_ms'])} | — |"
    )
    lines.append(
        f"| P95 最终延迟 | {fmt_ms(overall['p95_final_latency_ms'])} | — |"
    )
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
    failed_cases = [item for item in summary["worst_cases"] if not item["norm_exact_match"]][:8]

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
    report["report"] = {
        "format": "asr-report-format/v1",
        "engine": "WeNet",
        "config": {
            "mode": "single",
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


def main():
    args = parse_args()
    try:
        report = asyncio.run(run_batch(args))
        output_json = args.output_json or str(RESULTS_DIR / "wenet-results.json")
        output_csv = args.output_csv or str(RESULTS_DIR / "wenet-results.csv")
        output_md = args.output_md or str(RESULTS_DIR / "wenet-report.md")
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
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
