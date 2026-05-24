#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CORPUS_FILE="${CORPUS_FILE:-$ROOT_DIR/config/audio-corpus.txt}"
VERSIONS_FILE="${VERSIONS_FILE:-$ROOT_DIR/config/audio-versions.txt}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/audio}"
VERSION_FILTER="${VERSION:-all}"
ROLE_FILTER="${ROLE:-all}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

matches_filter() {
  local value="$1"
  local filter="$2"

  if [[ "$filter" == "all" ]]; then
    return 0
  fi

  IFS=',' read -r -a items <<<"$filter"
  for item in "${items[@]}"; do
    if [[ "$value" == "$item" ]]; then
      return 0
    fi
  done

  return 1
}

generate_version() {
  local version="$1"
  local voice="$2"
  local rate="$3"
  local notes="$4"
  local version_dir="$OUTPUT_DIR/$version"
  local manifest_file="$version_dir/manifest.csv"
  local count=0

  mkdir -p "$version_dir"
  printf 'id,role,intent,variant_type,index,text,version,voice,source,file_path,notes\n' >"$manifest_file"

  while IFS='|' read -r role field2 field3 field4 field5; do
    [[ -z "$role" ]] && continue
    [[ "$role" =~ ^# ]] && continue

    local intent=""
    local variant_type=""
    local index=""
    local text=""

    if [[ -n "${field5:-}" ]]; then
      intent="$field2"
      variant_type="$field3"
      index="$field4"
      text="$field5"
    else
      index="$field2"
      text="$field3"
    fi

    if ! matches_filter "$role" "$ROLE_FILTER"; then
      continue
    fi

    local role_dir="$version_dir/$role"
    local base_name="${role}_${index}"
    local tmp_file="$role_dir/$base_name.aiff"
    local wav_file="$role_dir/$base_name.wav"
    mkdir -p "$role_dir"

    say -v "$voice" -r "$rate" -o "$tmp_file" -- "$text"
    afconvert -f WAVE -d LEI16@16000 -c 1 "$tmp_file" "$wav_file"
    rm -f "$tmp_file"

    printf '%s,%s,%s,%s,%s,"%s",%s,%s,macos-say,%s,"%s"\n' \
      "$base_name" \
      "$role" \
      "$intent" \
      "$variant_type" \
      "$index" \
      "$text" \
      "$version" \
      "$voice" \
      "audio/$version/$role/$base_name.wav" \
      "$notes" >>"$manifest_file"

    count=$((count + 1))
  done <"$CORPUS_FILE"

  printf 'Generated %s wav files for version %s in %s\n' "$count" "$version" "$version_dir"
}

require_command say
require_command afconvert

if [[ ! -f "$CORPUS_FILE" ]]; then
  printf 'Corpus file not found: %s\n' "$CORPUS_FILE" >&2
  exit 1
fi

if [[ ! -f "$VERSIONS_FILE" ]]; then
  printf 'Versions file not found: %s\n' "$VERSIONS_FILE" >&2
  exit 1
fi

while IFS='|' read -r version voice rate notes; do
  [[ -z "$version" ]] && continue
  [[ "$version" =~ ^# ]] && continue

  if ! matches_filter "$version" "$VERSION_FILTER"; then
    continue
  fi

  generate_version "$version" "$voice" "$rate" "$notes"
done <"$VERSIONS_FILE"
