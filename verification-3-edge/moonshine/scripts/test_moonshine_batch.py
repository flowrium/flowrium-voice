#!/usr/bin/env python3

import argparse
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "verification-3-edge" / "common"))

from batch_eval import (
    build_report,
    default_manifests,
    levenshtein,
    load_rows,
    normalize,
    write_result_bundle,
)
from moonshine_voice import Transcriber, load_wav_file


ENGINE_DIR = ROOT_DIR / "verification-3-edge" / "moonshine"
MODELS_DIR = ENGINE_DIR / "models"
RESULTS_DIR = ENGINE_DIR / "results"
CACHE_DIR = ENGINE_DIR / "cache"

MODEL_CONFIGS = {
    "zh": {"model_dir": MODELS_DIR / "zh", "language": "zh"},
    "en": {"model_dir": MODELS_DIR / "en", "language": "en"},
}


def parse_args():
    parser = argparse.ArgumentParser(description="Batch-test audio manifests with Moonshine.")
    parser.add_argument("--model", default="zh", choices=sorted(MODEL_CONFIGS.keys()))
    parser.add_argument("--manifest", action="append", dest="manifests")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--version", action="append", dest="versions", default=[])
    parser.add_argument("--role", action="append", dest="roles", default=[])
    return parser.parse_args()


def detect_model_path(model_dir):
    directories = sorted(
        {
            path.parent
            for path in model_dir.rglob("encoder_model.ort")
        }
    )
    if directories:
        return directories[0]
    candidates = sorted([*model_dir.rglob("*.onnx"), *model_dir.rglob("*.bin")])
    if not candidates:
        raise FileNotFoundError(f"no model file found under {model_dir}")
    return candidates[0]


def transcribe_file(transcriber, file_path):
    audio_data, sample_rate = load_wav_file(file_path)
    audio_duration = len(audio_data) / sample_rate if sample_rate > 0 else 0.0
    start = time.perf_counter()
    transcript = transcriber.transcribe_without_streaming(audio_data, sample_rate=sample_rate, flags=0)
    elapsed = time.perf_counter() - start
    text = " ".join(line.text for line in transcript.lines).strip()

    return {
        "text": text,
        "rtf": round(elapsed / audio_duration, 4) if audio_duration > 0 else 0.0,
        "audio_duration_s": round(audio_duration, 3),
        "inference_time_s": round(elapsed, 4),
    }


def main():
    os.environ.setdefault("XDG_CACHE_HOME", str(CACHE_DIR))
    args = parse_args()
    model_dir = MODEL_CONFIGS[args.model]["model_dir"]
    model_path = detect_model_path(model_dir)
    transcriber = Transcriber(model_path=str(model_path))
    manifest_paths = [Path(path) for path in (args.manifests or default_manifests(ROOT_DIR))]
    rows = load_rows(ROOT_DIR, manifest_paths, args.versions, args.roles, args.limit)
    if not rows:
        raise SystemExit("No manifest rows matched the current filters.")

    language = MODEL_CONFIGS[args.model]["language"]
    results = []
    for index, row in enumerate(rows, start=1):
        try:
            transcription = transcribe_file(transcriber=transcriber, file_path=row["file_path"])
        except Exception as exc:
            print(f"[{index}/{len(rows)}] {row['id']} ERROR: {exc}", file=sys.stderr)
            continue

        expected = row["text"]
        actual = transcription["text"]
        expected_norm = normalize(expected)
        actual_norm = normalize(actual)
        char_distance = levenshtein(expected_norm, actual_norm)
        result = {
            "id": row["id"],
            "role": row["role"],
            "version": row["version"],
            "category": row["category"],
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
            **transcription,
        }
        results.append(result)
        print(
            f"[{index}/{len(rows)}] {row['id']} "
            f"exact={result['exact_match']} cer={result['cer']:.4f} rtf={result['rtf']:.4f}"
        )

    report = build_report(
        {
            "engine": "moonshine",
            "model": args.model,
            "language": language,
            "model_path": str(model_path),
            "manifest_paths": [str(path) for path in manifest_paths],
            "tested_count": len(results),
            "hotwords_enabled": False,
            "hotwords": [],
        },
        results,
        perf_key="rtf",
    )
    prefix = f"moonshine-{args.model}-no-hotword"
    config_line = (
        f"model={args.model}, language={language}, model_path={model_path}, "
        f"manifests={', '.join(str(path) for path in manifest_paths)}"
    )
    json_path, csv_path, md_path, markdown = write_result_bundle(
        RESULTS_DIR,
        prefix,
        report,
        engine_title=f"Moonshine {args.model}",
        config_line=config_line,
    )
    print()
    print(markdown)
    print(f"\nResults saved to {json_path}, {csv_path}, {md_path}")


if __name__ == "__main__":
    main()
