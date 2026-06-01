#!/usr/bin/env python3

import argparse
import json
import sys
import time
import wave
from pathlib import Path

import vosk

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "verification-3-edge" / "_cross-engine" / "common"))

from batch_eval import (
    build_report,
    default_manifests,
    levenshtein,
    load_rows,
    normalize,
    write_result_bundle,
)

ENGINE_DIR = ROOT_DIR / "verification-3-edge" / "vosk"
MODELS_DIR = ENGINE_DIR / "models"
RESULTS_DIR = ENGINE_DIR / "results"

MODEL_CONFIGS = {
    "small": {"path": MODELS_DIR / "vosk-model-small-cn-0.22"},
    "big": {"path": MODELS_DIR / "vosk-model-cn-0.22"},
}


def parse_args():
    parser = argparse.ArgumentParser(description="Batch-test audio manifests with Vosk.")
    parser.add_argument("--model", default="small", choices=sorted(MODEL_CONFIGS.keys()))
    parser.add_argument("--manifest", action="append", dest="manifests")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--version", action="append", dest="versions", default=[])
    parser.add_argument("--role", action="append", dest="roles", default=[])
    return parser.parse_args()


def transcribe_file(model, file_path):
    with wave.open(file_path, "rb") as wf:
        sample_rate = wf.getframerate()
        frame_count = wf.getnframes()
        pcm_data = wf.readframes(frame_count)
        audio_duration = frame_count / sample_rate if sample_rate > 0 else 0.0

    rec = vosk.KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    start = time.perf_counter()
    rec.AcceptWaveform(pcm_data)
    final_json = rec.FinalResult()
    elapsed = time.perf_counter() - start

    result = json.loads(final_json)
    text = result.get("text", "").strip()

    return {
        "text": text,
        "rtf": round(elapsed / audio_duration, 4) if audio_duration > 0 else 0.0,
        "audio_duration_s": round(audio_duration, 3),
        "inference_time_s": round(elapsed, 4),
    }


def main():
    vosk.SetLogLevel(-1)
    args = parse_args()

    config = MODEL_CONFIGS[args.model]
    model_path = str(config["path"])
    if not Path(model_path).exists():
        raise SystemExit(f"Model not found: {model_path}. Run setup/download_models.sh first.")
    model = vosk.Model(model_path=model_path)

    manifest_paths = [Path(path) for path in (args.manifests or default_manifests(ROOT_DIR))]
    rows = load_rows(ROOT_DIR, manifest_paths, args.versions, args.roles, args.limit)
    if not rows:
        raise SystemExit("No manifest rows matched the current filters.")

    results = []
    for index, row in enumerate(rows, start=1):
        try:
            transcription = transcribe_file(model, row["file_path"])
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
            "engine": "vosk",
            "model": args.model,
            "model_path": model_path,
            "manifest_paths": [str(path) for path in manifest_paths],
            "tested_count": len(results),
            "hotwords_enabled": False,
            "hotwords": [],
        },
        results,
        perf_key="rtf",
    )
    prefix = f"vosk-{args.model}-no-hotword"
    config_line = (
        f"model={args.model}, model_path={model_path}, "
        f"manifests={', '.join(str(path) for path in manifest_paths)}"
    )
    json_path, csv_path, md_path, markdown = write_result_bundle(
        RESULTS_DIR,
        prefix,
        report,
        engine_title=f"Vosk {args.model}",
        config_line=config_line,
    )
    print()
    print(markdown)
    print(f"\nResults saved to {json_path}, {csv_path}, {md_path}")


if __name__ == "__main__":
    main()
