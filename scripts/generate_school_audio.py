#!/usr/bin/env python3
"""
Generate school audio test data using edge-tts (cross-platform).
Replaces scripts/generate_school_audio.sh for Windows/macOS/Linux.

Usage:
  python scripts/generate_school_audio.py
  python scripts/generate_school_audio.py --version standard
  python scripts/generate_school_audio.py --role principal --role teacher
  python scripts/generate_school_audio.py --limit 10
"""

import argparse
import asyncio
import csv
import os
import sys
import wave
from pathlib import Path

try:
    import edge_tts
except ImportError:
    raise SystemExit(
        "Missing dependency: edge-tts is not installed.\n"
        "Install it with: pip install edge-tts\n"
        "Or on Windows: pip install edge-tts"
    )

ROOT_DIR = Path(__file__).resolve().parent.parent
CORPUS_FILE = ROOT_DIR / "config" / "audio-corpus.txt"
VERSIONS_FILE = ROOT_DIR / "config" / "audio-versions.txt"
OUTPUT_DIR = ROOT_DIR / "audio"

# Mapping from friendly voice names (used in audio-versions.txt) to edge-tts voices
VOICE_MAP = {
    "Tingting": "zh-CN-XiaoxiaoNeural",
    "Xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "Yunxi": "zh-CN-YunxiNeural",
    "Yunyang": "zh-CN-YunyangNeural",
    "Xiaoyi": "zh-CN-XiaoyiNeural",
    "Yunjian": "zh-CN-YunjianNeural",
}

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

# Rough conversion from macOS say WPM to edge-tts +/- percentage
# macOS say default ~200 WPM, edge-tts default ~150 WPM for Chinese
# rate=185 -> +20%, rate=165 -> +0%, rate=200 -> +30%
def wpm_to_edge_rate(wpm):
    if wpm >= 200:
        return "+30%"
    elif wpm >= 185:
        return "+20%"
    elif wpm >= 170:
        return "+10%"
    elif wpm >= 150:
        return "+0%"
    else:
        return "-10%"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate school audio test data using edge-tts."
    )
    parser.add_argument(
        "--version",
        default="all",
        help="Only generate matching versions (comma separated, e.g. standard,humanized). Default: all",
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
        help="Only generate the first N rows per version. 0 means all rows.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Base output directory. Default: audio/",
    )
    parser.add_argument(
        "--corpus-file",
        default=str(CORPUS_FILE),
        help="Corpus file path.",
    )
    parser.add_argument(
        "--versions-file",
        default=str(VERSIONS_FILE),
        help="Versions config file path.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip generating WAV files that already exist.",
    )
    parser.add_argument(
        "--voice-override",
        help="Override voice for all versions (edge-tts name, e.g. zh-CN-XiaoyiNeural).",
    )
    return parser.parse_args()


def matches_filter(value, filter_spec):
    if filter_spec == "all":
        return True
    return value in filter_spec.split(",")


def load_versions(versions_path, version_filter):
    entries = []
    with open(versions_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) >= 4:
                version, voice, rate_str, notes = parts[0], parts[1], parts[2], parts[3]
            else:
                continue
            if matches_filter(version, version_filter):
                entries.append({
                    "version": version,
                    "voice": voice,
                    "rate": int(rate_str),
                    "notes": notes.strip(),
                })
    return entries


def load_corpus(corpus_path, roles):
    rows = []
    with open(corpus_path, encoding="utf-8") as f:
        for raw_line in f:
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
                continue
            if not roles or role in roles:
                rows.append({
                    "role": role,
                    "intent": intent,
                    "variant_type": variant_type,
                    "index": index,
                    "text": text,
                })
    return rows


async def generate_version(version_entry, corpus_rows, output_base, skip_existing, voice_override):
    version = version_entry["version"]
    voice_name = version_entry["voice"]
    rate_wpm = version_entry["rate"]
    notes = version_entry["notes"]

    voice = voice_override or VOICE_MAP.get(voice_name, DEFAULT_VOICE)
    rate_str = wpm_to_edge_rate(rate_wpm)

    version_dir = output_base / version
    version_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = version_dir / "manifest.csv"

    count = 0
    written_rows = []

    for row in corpus_rows:
        role = row["role"]
        base_name = f"{role}_{row['index']}"
        role_dir = version_dir / role
        role_dir.mkdir(parents=True, exist_ok=True)
        wav_path = role_dir / f"{base_name}.wav"

        if skip_existing and wav_path.exists():
            print(f"[{base_name}] skipped (exists)")
        else:
            text = row["text"]
            tts = edge_tts.Communicate(text, voice=voice, rate=rate_str)
            print(f"[{base_name}] generating ({voice}, rate={rate_str})...")
            await _generate_wav(tts, wav_path)

        manifest_row = {
            "id": base_name,
            "role": role,
            "intent": row["intent"],
            "variant_type": row["variant_type"],
            "index": row["index"],
            "text": row["text"],
            "version": version,
            "voice": voice_name,
            "source": "edge-tts",
            "file_path": f"audio/{version}/{role}/{base_name}.wav",
            "notes": notes,
        }
        written_rows.append(manifest_row)
        count += 1

    with open(manifest_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "id", "role", "intent", "variant_type", "index", "text",
            "version", "voice", "source", "file_path", "notes",
        ])
        writer.writeheader()
        writer.writerows(written_rows)

    print(f"Generated {count} wav files for version {version} in {version_dir}")
    return count


async def _generate_wav(tts, wav_path):
    """Generate WAV from edge-tts, converting MP3 stream to 16kHz mono WAV."""
    # edge-tts streams MP3 audio; capture it and convert to WAV
    mp3_data = bytearray()
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            mp3_data.extend(chunk["data"])

    if not mp3_data:
        # fallback: maybe save() works directly (rare edge case)
        await tts.save(str(wav_path))
        return

    # Try ffmpeg to convert MP3 bytes to 16kHz mono WAV
    import subprocess
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", "pipe:0",
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-f", "wav", str(wav_path),
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        await proc.communicate(input=bytes(mp3_data))
        if proc.returncode == 0 and wav_path.exists():
            return
    except FileNotFoundError:
        pass

    # Fallback: write raw data and try wave re-encoding
    wav_path.write_bytes(bytes(mp3_data))
    import audioop
    try:
        with wave.open(str(wav_path), "rb") as w:
            frames = w.readframes(w.getnframes())
            channels = w.getnchannels()
            sampwidth = w.getsampwidth()
            rate = w.getframerate()
        if channels > 1:
            frames = audioop.tomono(frames, sampwidth, 0.5, 0.5)
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(sampwidth)
            w.setframerate(rate)
            w.writeframes(frames)
    except Exception as exc:
        print(f"  Warning: could not convert audio for {wav_path}: {exc}", file=sys.stderr)


async def main():
    args = parse_args()
    output_base = Path(args.output_dir).resolve()
    corpus_path = Path(args.corpus_file).resolve()
    versions_path = Path(args.versions_file).resolve()

    if not corpus_path.exists():
        raise SystemExit(f"Corpus file not found: {corpus_path}")
    if not versions_path.exists():
        raise SystemExit(f"Versions file not found: {versions_path}")

    versions = load_versions(versions_path, args.version)
    if not versions:
        raise SystemExit(f"No matching versions found in {versions_path}")

    corpus_rows = load_corpus(corpus_path, args.role)
    if not corpus_rows:
        raise SystemExit(f"No corpus rows matched the current role filter: {args.role}")

    if args.limit > 0:
        corpus_rows = corpus_rows[:args.limit]

    total = 0
    for version_entry in versions:
        count = await generate_version(
            version_entry, corpus_rows, output_base,
            args.skip_existing, args.voice_override,
        )
        total += count

    print(f"\nDone! Generated {total} wav files total in {output_base}")


if __name__ == "__main__":
    asyncio.run(main())