#!/usr/bin/env python3

import argparse
import csv
import json
import os
import re
import statistics
import sys
import time
import wave
from collections import defaultdict
from pathlib import Path

import numpy as np
import sherpa_onnx


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_MANIFESTS = [
    ROOT_DIR / "audio/standard/manifest.csv",
    ROOT_DIR / "audio/humanized/manifest.csv",
    ROOT_DIR / "audio/myvoice/manifest.csv",
]
MODELS_DIR = ROOT_DIR / "verification-3-edge/sherpa-onnx/models"
RESULTS_DIR = ROOT_DIR / "verification-3-edge/sherpa-onnx/results"
HOTWORDS_FILE = ROOT_DIR / "config/hotwords.txt"
PUNC_RE = re.compile(r'[\s，。！？；：、"""''（）()\[\]【】,.!?;:"\-]')

MODEL_CONFIGS = {
    "paraformer": {
        "model_dir": MODELS_DIR / "paraformer-zh-int8",
        "model_files": {"paraformer": "model.int8.onnx"},
        "recognizer_type": "offline",
        "factory": "from_paraformer",
        "supports_hotword": False,
    },
    "sensevoice": {
        "model_dir": MODELS_DIR / "sense-voice-zh-int8",
        "model_files": {"model": "model.int8.onnx"},
        "recognizer_type": "offline",
        "factory": "from_sense_voice",
        "supports_hotword": False,
        "extra_kwargs": {"language": "auto", "use_itn": True},
    },
    "transducer": {
        "model_dir": MODELS_DIR / "zipformer-transducer-zh-int8",
        "model_files": {
            "encoder": "encoder.int8.onnx",
            "decoder": "decoder.onnx",
            "joiner": "joiner.int8.onnx",
        },
        "recognizer_type": "online",
        "factory": "from_transducer",
        "supports_hotword": True,
        "default_decoding_method": "greedy_search",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch-test audio manifests with Sherpa-ONNX quantized models."
    )
    parser.add_argument(
        "--model",
        default="paraformer",
        choices=["paraformer", "sensevoice", "transducer"],
        help="Model to use. Default: paraformer",
    )
    parser.add_argument(
        "--manifest",
        action="append",
        dest="manifests",
        help="Manifest CSV path. Repeatable. Defaults to all manifests.",
    )
    parser.add_argument(
        "--hotword",
        action="append",
        default=[],
        help="Hotword. Repeatable. Only transducer currently supports hotwords.",
    )
    parser.add_argument(
        "--hotwords-file",
        default=str(HOTWORDS_FILE),
        help="Hotwords file path (one word per line). Default: config/hotwords.txt",
    )
    parser.add_argument(
        "--use-hotwords-file",
        action="store_true",
        help="Load hotwords from --hotwords-file. Only effective for transducer.",
    )
    parser.add_argument(
        "--decoding-method",
        choices=["greedy_search", "modified_beam_search"],
        default="",
        help="Transducer decoding method. Default: auto (greedy_search without hotwords, modified_beam_search with hotwords).",
    )
    parser.add_argument(
        "--max-active-paths",
        type=int,
        default=4,
        help="Transducer max active paths for modified_beam_search. Default: 4",
    )
    parser.add_argument(
        "--hotwords-score",
        type=float,
        default=1.5,
        help="Transducer hotword bias score. Default: 1.5",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only test the first N rows. 0 means all.",
    )
    parser.add_argument(
        "--version",
        action="append",
        dest="versions",
        default=[],
        help="Filter by version. Repeatable.",
    )
    parser.add_argument(
        "--role",
        action="append",
        dest="roles",
        default=[],
        help="Filter by role. Repeatable.",
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


def load_hotwords_file(path):
    path = Path(path)
    if not path.exists():
        print(f"Warning: hotwords file not found: {path}", file=sys.stderr)
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def resolve_hotwords(args, model_name):
    hotwords = list(args.hotword)
    if args.use_hotwords_file:
        hotwords.extend(load_hotwords_file(args.hotwords_file))

    deduped = []
    seen = set()
    for word in hotwords:
        if word not in seen:
            deduped.append(word)
            seen.add(word)

    if deduped and not MODEL_CONFIGS[model_name]["supports_hotword"]:
        print(f"Warning: {model_name} does not support hotwords, ignoring hotword settings", file=sys.stderr)
        return []

    return deduped


def resolve_decoding_method(args, model_name, hotwords):
    config = MODEL_CONFIGS[model_name]
    if config["factory"] != "from_transducer":
        return ""

    method = args.decoding_method or config.get("default_decoding_method", "greedy_search")
    if hotwords and not args.decoding_method:
        method = "modified_beam_search"

    if hotwords and method != "modified_beam_search":
        raise SystemExit("Transducer hotwords require --decoding-method modified_beam_search")

    return method


def create_recognizer(model_name, hotwords=None, decoding_method="", max_active_paths=4, hotwords_score=1.5):
    config = MODEL_CONFIGS[model_name]
    model_dir = config["model_dir"]
    tokens_path = model_dir / "tokens.txt"

    missing_files = []
    for filename in config["model_files"].values():
        model_path = model_dir / filename
        if not model_path.exists():
            missing_files.append(str(model_path))
    if not tokens_path.exists():
        missing_files.append(str(tokens_path))
    if missing_files:
        raise FileNotFoundError(
            "Model files not found:\n- " + "\n- ".join(missing_files) + "\nRun download_models.sh first."
        )

    kwargs = {"tokens": str(tokens_path), "num_threads": 4, "provider": "cpu"}
    for param_name, filename in config["model_files"].items():
        kwargs[param_name] = str(model_dir / filename)
    kwargs.update(config.get("extra_kwargs", {}))
    if config["factory"] == "from_transducer":
        kwargs["decoding_method"] = decoding_method
        kwargs["max_active_paths"] = max_active_paths
        kwargs["hotwords_score"] = hotwords_score

    recognizer_cls = sherpa_onnx.OfflineRecognizer
    if config.get("recognizer_type") == "online":
        recognizer_cls = sherpa_onnx.OnlineRecognizer

    factory = getattr(recognizer_cls, config["factory"])
    recognizer = factory(**kwargs)

    if hotwords and config["supports_hotword"]:
        hotwords_str = "\n".join(hotwords) + "\n"

        def create_stream_with_hotwords():
            return recognizer.create_stream(hotwords=hotwords_str)

        return recognizer, create_stream_with_hotwords
    else:
        if hotwords and not config["supports_hotword"]:
            print(f"Warning: {model_name} does not support hotwords, ignoring --hotword", file=sys.stderr)

        return recognizer, recognizer.create_stream


def transcribe_file(recognizer, create_stream, file_path, recognizer_type):
    with wave.open(file_path, "rb") as f:
        sample_rate = f.getframerate()
        frame_count = f.getnframes()
        frames = f.readframes(frame_count)
        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        audio_duration = frame_count / sample_rate

    stream = create_stream()
    stream.accept_waveform(sample_rate, samples.tolist())

    start_time = time.perf_counter()
    if recognizer_type == "online":
        stream.input_finished()
        while recognizer.is_ready(stream):
            recognizer.decode_stream(stream)
        text = recognizer.get_result(stream)
    else:
        recognizer.decode_stream(stream)
        text = stream.result.text
    elapsed = time.perf_counter() - start_time
    rtf = elapsed / audio_duration if audio_duration > 0 else 0.0

    return {
        "text": text,
        "rtf": round(rtf, 4),
        "audio_duration_s": round(audio_duration, 3),
        "inference_time_s": round(elapsed, 4),
    }


def summarize(items):
    total = len(items)
    if total == 0:
        return {
            "count": 0,
            "passed": 0,
            "norm_exact_match_rate": 0.0,
            "cer": 0.0,
            "avg_rtf": 0.0,
            "p95_rtf": 0.0,
        }

    norm_exact_matches = sum(1 for item in items if item["norm_exact_match"])
    expected_chars = sum(item["expected_chars"] for item in items)
    char_distance = sum(item["char_distance"] for item in items)
    rtfs = sorted(item["rtf"] for item in items)
    p95_index = max(0, min(total - 1, int(total * 0.95) - 1))

    return {
        "count": total,
        "passed": norm_exact_matches,
        "norm_exact_match_rate": round(norm_exact_matches / total, 4),
        "cer": round(char_distance / expected_chars, 4) if expected_chars else 0.0,
        "avg_rtf": round(statistics.mean(rtfs), 4),
        "p95_rtf": rtfs[p95_index],
    }


def run_batch(args):
    manifest_paths = [Path(p) for p in (args.manifests or DEFAULT_MANIFESTS)]
    rows = load_rows(manifest_paths, args.versions, args.roles, args.limit)
    if not rows:
        raise SystemExit("No manifest rows matched the current filters.")

    model_name = args.model
    hotwords = resolve_hotwords(args, model_name)
    decoding_method = resolve_decoding_method(args, model_name, hotwords)
    use_hotwords = bool(hotwords) and MODEL_CONFIGS[model_name]["supports_hotword"]
    hw_label = "hotword" if use_hotwords else "no-hotword"
    recognizer_type = MODEL_CONFIGS[model_name].get("recognizer_type", "offline")

    recognizer, create_stream = create_recognizer(
        model_name,
        hotwords if use_hotwords else None,
        decoding_method=decoding_method,
        max_active_paths=args.max_active_paths,
        hotwords_score=args.hotwords_score,
    )
    results = []

    for index, row in enumerate(rows, start=1):
        try:
            transcription = transcribe_file(recognizer, create_stream, row["file_path"], recognizer_type)
        except Exception as exc:
            print(f"[{index}/{len(rows)}] {row['id']} ERROR: {exc}", file=sys.stderr)
            continue

        expected = row["text"]
        actual = transcription["text"]
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
            "rtf": transcription["rtf"],
            "audio_duration_s": transcription["audio_duration_s"],
            "inference_time_s": transcription["inference_time_s"],
        }
        results.append(result)
        print(
            f"[{index}/{len(rows)}] {row['id']} "
            f"exact={result['exact_match']} cer={result['cer']:.4f} "
            f"rtf={result['rtf']:.4f}"
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
            "model": model_name,
            "recognizer_type": recognizer_type,
            "decoding_method": decoding_method,
            "hotwords": hotwords if use_hotwords else [],
            "hotwords_enabled": use_hotwords,
            "manifest_paths": [str(p) for p in manifest_paths],
            "tested_count": len(results),
        },
        "summary": {
            "overall": summarize(results),
            "by_version": {k: summarize(v) for k, v in sorted(by_version.items())},
            "by_role": {k: summarize(v) for k, v in sorted(by_role.items())},
            "by_category": {k: summarize(v) for k, v in sorted(by_category.items())},
            "worst_cases": sorted(
                results, key=lambda item: (item["cer"], item["char_distance"]), reverse=True
            )[:15],
        },
        "results": results,
    }
    return report


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_csv(path, items):
    fieldnames = [
        "id", "role", "version", "category", "file_path",
        "expected", "actual", "exact_match", "norm_exact_match",
        "char_distance", "expected_chars", "cer",
        "rtf", "audio_duration_s", "inference_time_s",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in items:
            writer.writerow({k: row.get(k) for k in fieldnames})


def _fmt_pct(val):
    return f"{val:.2%}"


def build_markdown_report(report):
    meta = report["meta"]
    summary = report["summary"]
    overall = summary["overall"]
    model_name = meta["model"]
    recognizer_type = meta.get("recognizer_type", "offline")
    hw_label = "有热词" if meta["hotwords_enabled"] else "无热词"
    manifests = ", ".join(meta["manifest_paths"])
    decoding_method = meta.get("decoding_method") or "(n/a)"
    failed_cases = [item for item in summary["worst_cases"] if not item["norm_exact_match"]][:8]

    lines = []
    lines.append(f"## Sherpa-ONNX {model_name} Test Results")
    lines.append("")
    lines.append(
        f"**Config**: model={model_name}, recognizer={recognizer_type}, decoding={decoding_method}, hotwords={hw_label}, manifests={manifests}"
    )
    lines.append("")
    lines.append("### Overall")
    lines.append("| Metric | Value | Note |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| 测试总数 | {overall['count']} | |")
    lines.append(f"| 成功条数 | {overall['passed']} | 归一化后完全匹配 |")
    lines.append(f"| **成功率** | **{_fmt_pct(overall['norm_exact_match_rate'])}** | 成功条数/总条数 |")
    lines.append(f"| CER | {_fmt_pct(overall['cer'])} | 字符错误率 |")
    lines.append(f"| 平均 RTF | {overall['avg_rtf']:.4f} | <1.0 表示快于实时 |")
    lines.append(f"| P95 RTF | {overall['p95_rtf']:.4f} | |")
    lines.append("")

    lines.append("### By Role")
    lines.append("| Role | Count | 成功数 | **成功率** | CER | Avg RTF |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for role, value in summary["by_role"].items():
        lines.append(
            f"| {role} | {value['count']} | {value['passed']} "
            f"| **{_fmt_pct(value['norm_exact_match_rate'])}** "
            f"| {_fmt_pct(value['cer'])} | {value['avg_rtf']:.4f} |"
        )
    lines.append("")

    lines.append("### By Version")
    lines.append("| Version | Count | 成功数 | **成功率** | CER | Avg RTF |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for version, value in summary["by_version"].items():
        lines.append(
            f"| {version} | {value['count']} | {value['passed']} "
            f"| **{_fmt_pct(value['norm_exact_match_rate'])}** "
            f"| {_fmt_pct(value['cer'])} | {value['avg_rtf']:.4f} |"
        )
    lines.append("")

    lines.append("### Failed Cases (top 8)")
    lines.append("| ID | Expected | Actual | CER |")
    lines.append("| --- | --- | --- | --- |")
    for item in failed_cases:
        lines.append(
            f"| {item['id']} | {item['expected']} | {item['actual']} | {_fmt_pct(item['cer'])} |"
        )
    if not failed_cases:
        lines.append("| — | — | — | — |")
    lines.append("")
    return "\n".join(lines)


def main():
    args = parse_args()
    model_name = args.model
    hotwords = resolve_hotwords(args, model_name)
    use_hotwords = bool(hotwords) and MODEL_CONFIGS[model_name]["supports_hotword"]
    hw_label = "hotword" if use_hotwords else "no-hotword"

    report = run_batch(args)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"sherpa-onnx-{model_name}-{hw_label}"
    json_path = RESULTS_DIR / f"{suffix}-results.json"
    csv_path = RESULTS_DIR / f"{suffix}-results.csv"
    md_path = RESULTS_DIR / f"{suffix}-report.md"

    write_json(json_path, report)
    write_csv(csv_path, report["results"])
    markdown = build_markdown_report(report)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print()
    print(markdown)
    print(f"\nResults saved to {json_path}, {csv_path}, {md_path}")


if __name__ == "__main__":
    main()
