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


ENGINE_DIR = ROOT_DIR / "verification-3-edge" / "moonshine"
MODELS_DIR = ENGINE_DIR / "models"
RESULTS_DIR = ENGINE_DIR / "results"
DEFAULT_CLI = ENGINE_DIR / "vendor" / "moonshine" / "moonshine-onnx" / "cli-transcriber.py"

MODEL_CONFIGS = {
    "mandarin": {"model_dir": MODELS_DIR / "mandarin", "language": "zh"},
    "english": {"model_dir": MODELS_DIR / "english", "language": "en"},
}


def parse_args():
    parser = argparse.ArgumentParser(description="Batch-test audio manifests with Moonshine.")
    parser.add_argument("--model", default="mandarin", choices=sorted(MODEL_CONFIGS.keys()))
    parser.add_argument("--manifest", action="append", dest="manifests")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--version", action="append", dest="versions", default=[])
    parser.add_argument("--role", action="append", dest="roles", default=[])
    parser.add_argument("--moonshine-cli", default=str(DEFAULT_CLI))
    parser.add_argument("--model-arch", default="")
    return parser.parse_args()


def read_audio_duration(file_path):
    with wave.open(file_path, "rb") as handle:
        return handle.getnframes() / handle.getframerate()


def detect_model_path(model_dir):
    candidates = sorted(model_dir.rglob("*.onnx"))
    if not candidates:
        raise FileNotFoundError(f"no .onnx model found under {model_dir}")
    return candidates[0]


def transcribe_file(cli_path, model_path, language, model_arch, file_path):
    audio_duration = read_audio_duration(file_path)
    with tempfile.TemporaryDirectory(prefix="moonshine-") as temp_dir:
        out_path = Path(temp_dir) / "result.txt"
        command = [
            "python3",
            str(cli_path),
            "--language",
            language,
            "--model_path",
            str(model_path),
            "--text_output",
            str(out_path),
        ]
        if model_arch:
            command.extend(["--model_arch", model_arch])
        command.append(file_path)

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
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "moonshine CLI failed")
        if not out_path.exists():
            raise RuntimeError(f"expected transcript not produced: {out_path}")
        text = out_path.read_text(encoding="utf-8", errors="replace").strip()

    return {
        "text": text,
        "rtf": round(elapsed / audio_duration, 4) if audio_duration > 0 else 0.0,
        "audio_duration_s": round(audio_duration, 3),
        "inference_time_s": round(elapsed, 4),
    }


def main():
    args = parse_args()
    cli_path = Path(args.moonshine_cli)
    if not cli_path.exists():
        raise SystemExit(f"Moonshine CLI not found: {cli_path}")

    model_dir = MODEL_CONFIGS[args.model]["model_dir"]
    model_path = detect_model_path(model_dir)
    manifest_paths = [Path(path) for path in (args.manifests or default_manifests(ROOT_DIR))]
    rows = load_rows(ROOT_DIR, manifest_paths, args.versions, args.roles, args.limit)
    if not rows:
        raise SystemExit("No manifest rows matched the current filters.")

    language = MODEL_CONFIGS[args.model]["language"]
    results = []
    for index, row in enumerate(rows, start=1):
        try:
            transcription = transcribe_file(
                cli_path=cli_path,
                model_path=model_path,
                language=language,
                model_arch=args.model_arch,
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
            "engine": "moonshine",
            "model": args.model,
            "language": language,
            "model_path": str(model_path),
            "model_arch": args.model_arch,
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
