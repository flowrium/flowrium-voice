#!/usr/bin/env python3

import argparse
import csv
import os
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
CORPUS_FILE = ROOT_DIR / "config/audio-corpus.txt"
OUTPUT_DIR = ROOT_DIR / "audio"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a voice-cloned audio version from a reference WAV."
    )
    parser.add_argument(
        "--reference-wav",
        required=True,
        help="Reference voice WAV path.",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Output version name, for example myvoice.",
    )
    parser.add_argument(
        "--language",
        default="zh-cn",
        help="XTTS language code. Default: zh-cn",
    )
    parser.add_argument(
        "--corpus-file",
        default=str(CORPUS_FILE),
        help="Corpus file in role|index|text format.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Base output directory. Default: audio/",
    )
    parser.add_argument(
        "--role",
        action="append",
        default=[],
        help="Only generate matching roles. Repeatable.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only generate the first N matched rows. 0 means all rows.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip generating WAV files that already exist on disk.",
    )
    return parser.parse_args()


def require_dependency():
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib-cache")
    try:
        from TTS.api import TTS  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: Coqui TTS is not installed in the current Python "
            "environment. Install it first, then rerun this script."
        ) from exc


def matches_filter(value, filters):
    return not filters or value in filters


def ensure_reference_wav(source_path):
    temp_dir = tempfile.mkdtemp(prefix="flowrium-voice-ref-")
    normalized_path = Path(temp_dir) / "reference_24000_mono.wav"
    cmd = [
        "afconvert",
        "-f",
        "WAVE",
        "-d",
        "LEI16@24000",
        "-c",
        "1",
        str(source_path),
        str(normalized_path),
    ]
    subprocess.run(cmd, check=True)

    source_duration = get_wav_duration_seconds(source_path)
    normalized_duration = get_wav_duration_seconds(normalized_path)

    if (
        source_duration is None
        or normalized_duration is None
        or normalized_duration < 1.0
        or normalized_duration < source_duration * 0.5
    ):
        print(
            "Warning: normalized reference WAV looks truncated; "
            "falling back to the original reference audio.",
            file=sys.stderr,
        )
        return source_path

    return normalized_path


def get_wav_duration_seconds(path):
    try:
        with wave.open(str(path), "rb") as wav_file:
            frame_count = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            if sample_rate <= 0:
                return None
            return frame_count / sample_rate
    except (wave.Error, FileNotFoundError):
        return None


def load_corpus_rows(corpus_path, roles):
    rows = []
    with open(corpus_path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) == 5:
                role, intent, variant_type, index, text = parts
            elif len(parts) == 3:
                role, index, text = parts
                intent = ""
                variant_type = ""
            else:
                raise ValueError(f"Unexpected corpus row: {line}")
            if matches_filter(role, roles):
                rows.append(
                    {
                        "role": role,
                        "intent": intent,
                        "variant_type": variant_type,
                        "index": index,
                        "text": text,
                    }
                )
    return rows


def main():
    args = parse_args()
    require_dependency()
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib-cache")

    from TTS.api import TTS

    reference_wav = Path(args.reference_wav).resolve()
    if not reference_wav.exists():
        raise SystemExit(f"Reference WAV not found: {reference_wav}")

    corpus_path = Path(args.corpus_file).resolve()
    if not corpus_path.exists():
        raise SystemExit(f"Corpus file not found: {corpus_path}")

    output_base = Path(args.output_dir).resolve()
    version_dir = output_base / args.version
    version_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = version_dir / "manifest.csv"

    rows = load_corpus_rows(corpus_path, args.role)
    if args.limit > 0:
        rows = rows[: args.limit]
    if not rows:
        raise SystemExit("No corpus rows matched the current filters.")

    normalized_reference = ensure_reference_wav(reference_wav)
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    with open(manifest_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "role",
                "intent",
                "variant_type",
                "index",
                "text",
                "version",
                "voice",
                "source",
                "file_path",
                "notes",
            ]
        )

        for position, row in enumerate(rows, start=1):
            role_dir = version_dir / row["role"]
            role_dir.mkdir(parents=True, exist_ok=True)
            base_name = f"{row['role']}_{row['index']}"
            wav_path = role_dir / f"{base_name}.wav"

            if args.skip_existing and wav_path.exists():
                print(f"[{position}/{len(rows)}] skipping {base_name} (exists)")
            else:
                print(f"[{position}/{len(rows)}] generating {base_name}")
                tts.tts_to_file(
                    text=row["text"],
                    speaker_wav=str(normalized_reference),
                    language=args.language,
                    file_path=str(wav_path),
                )

            writer.writerow(
                [
                    base_name,
                    row["role"],
                    row["intent"],
                    row["variant_type"],
                    row["index"],
                    row["text"],
                    args.version,
                    reference_wav.stem,
                    "coqui-xtts-v2",
                    str(wav_path.relative_to(ROOT_DIR)),
                    f"reference={reference_wav.name}; language={args.language}",
                ]
            )

    print(f"Generated {len(rows)} wav files in {version_dir}")
    print(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Audio conversion failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
