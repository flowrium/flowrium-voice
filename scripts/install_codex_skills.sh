#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_SKILLS_DIR="${REPO_ROOT}/.codex/skills"
TARGET_ROOT="${HOME}/.codex/skills"

if [[ ! -d "${PROJECT_SKILLS_DIR}" ]]; then
  echo "Project skills directory not found: ${PROJECT_SKILLS_DIR}" >&2
  exit 1
fi

mkdir -p "${TARGET_ROOT}"

installed=0

while IFS= read -r -d '' skill_path; do
  skill_name="$(basename "${skill_path}")"
  target_link="${TARGET_ROOT}/${skill_name}"

  ln -sfn "${skill_path}" "${target_link}"
  echo "linked ${target_link} -> ${skill_path}"
  installed=$((installed + 1))
done < <(find "${PROJECT_SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type l -print0 | sort -z)

echo "installed ${installed} Codex skill(s)"
