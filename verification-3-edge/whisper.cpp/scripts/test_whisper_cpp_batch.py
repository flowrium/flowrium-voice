#!/usr/bin/env python3

import argparse
import subprocess
import sys
import tempfile
import time
import wave
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


ENGINE_DIR = ROOT_DIR / "verification-3-edge" / "whisper.cpp"
MODELS_DIR = ENGINE_DIR / "models"
RESULTS_DIR = ENGINE_DIR / "results"
DEFAULT_CLI = ENGINE_DIR / "vendor" / "whisper.cpp" / "build" / "bin" / "whisper-cli"

MODEL_CONFIGS = {
    "base": {"filename": "ggml-base.bin", "download_name": "base"},
    "small": {"filename": "ggml-small.bin", "download_name": "small"},
    "large-v3-turbo": {
        "filename": "ggml-large-v3-turbo-q5_0.bin",
        "download_name": "large-v3-turbo-q5_0",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(description="Batch-test audio manifests with whisper.cpp.")
    parser.add_argument("--model", default="base", choices=sorted(MODEL_CONFIGS.keys()))
    parser.add_argument("--manifest", action="append", dest="manifests")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--version", action="append", dest="versions", default=[])
    parser.add_argument("--role", action="append", dest="roles", default=[])
    parser.add_argument("--language", default="zh")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--whisper-cli", default=str(DEFAULT_CLI))
    return parser.parse_args()


def read_audio_duration(file_path):
    with wave.open(file_path, "rb") as handle:
        return handle.getnframes() / handle.getframerate()


def transcribe_file(cli_path, model_path, language, threads, row_id, file_path):
    audio_duration = read_audio_duration(file_path)
    with tempfile.TemporaryDirectory(prefix=f"whisper-cpp-{row_id}-") as temp_dir:
        out_prefix = Path(temp_dir) / "result"
        command = [
            str(cli_path),
            "-m",
            str(model_path),
            "-f",
            file_path,
            "-l",
            language,
            "-t",
            str(threads),
            "-nt",
            "-ng",
            "-nfa",
            "-otxt",
            "-of",
            str(out_prefix),
        ]
        start = time.perf_counter()
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        elapsed = time.perf_counter() - start
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "whisper-cli failed")

        transcript_path = out_prefix.with_suffix(".txt")
        if transcript_path.exists():
            text = transcript_path.read_text(encoding="utf-8", errors="replace").strip()
        else:
            text = completed.stdout.strip().splitlines()[-1].strip() if completed.stdout.strip() else ""

    return {
        "text": text,
        "rtf": round(elapsed / audio_duration, 4) if audio_duration > 0 else 0.0,
        "audio_duration_s": round(audio_duration, 3),
        "inference_time_s": round(elapsed, 4),
    }


def main():
    args = parse_args()
    cli_path = Path(args.whisper_cli)
    if not cli_path.exists():
        raise SystemExit(f"whisper-cli not found: {cli_path}")

    model_path = MODELS_DIR / MODEL_CONFIGS[args.model]["filename"]
    if not model_path.exists():
        raise SystemExit(f"model not found: {model_path}. Run setup/download_models.sh first.")

    manifest_paths = [Path(path) for path in (args.manifests or default_manifests(ROOT_DIR))]
    rows = load_rows(ROOT_DIR, manifest_paths, args.versions, args.roles, args.limit)
    if not rows:
        raise SystemExit("No manifest rows matched the current filters.")

    results = []
    for index, row in enumerate(rows, start=1):
        try:
            transcription = transcribe_file(
                cli_path=cli_path,
                model_path=model_path,
                language=args.language,
                threads=args.threads,
                row_id=row["id"],
                file_path=row["file_path"],
            )
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
            "engine": "whisper.cpp",
            "model": args.model,
            "language": args.language,
            "threads": args.threads,
            "manifest_paths": [str(path) for path in manifest_paths],
            "tested_count": len(results),
            "hotwords_enabled": False,
            "hotwords": [],
        },
        results,
        perf_key="rtf",
    )
    prefix = f"whisper-cpp-{args.model}-no-hotword"
    config_line = (
        f"model={args.model}, language={args.language}, threads={args.threads}, "
        f"manifests={', '.join(str(path) for path in manifest_paths)}"
    )
    json_path, csv_path, md_path, markdown = write_result_bundle(
        RESULTS_DIR,
        prefix,
        report,
        engine_title=f"whisper.cpp {args.model}",
        config_line=config_line,
    )
    print()
    print(markdown)
    print(f"\nResults saved to {json_path}, {csv_path}, {md_path}")


if __name__ == "__main__":
    main()
