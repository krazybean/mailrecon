#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: ./release.sh {patch|minor|major}"
  exit 1
fi

bump_type="$1"

case "$bump_type" in
  patch|minor|major)
    ;;
  *)
    echo "Error: version bump must be one of: patch, minor, major"
    exit 1
    ;;
esac

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: working directory is dirty"
  exit 1
fi

version_line="$(grep -E '^version = "[0-9]+\.[0-9]+\.[0-9]+"' pyproject.toml | head -n 1)"

if [[ -z "$version_line" ]]; then
  echo "Error: could not find version in pyproject.toml"
  exit 1
fi

old_version="$(printf '%s\n' "$version_line" | sed -E 's/version = "([0-9]+\.[0-9]+\.[0-9]+)"/\1/')"
IFS='.' read -r major minor patch <<< "$old_version"

case "$bump_type" in
  patch)
    patch=$((patch + 1))
    ;;
  minor)
    minor=$((minor + 1))
    patch=0
    ;;
  major)
    major=$((major + 1))
    minor=0
    patch=0
    ;;
esac

new_version="${major}.${minor}.${patch}"

echo "Old version: $old_version"
echo "New version: $new_version"

python - <<'PY' "$old_version" "$new_version"
from pathlib import Path
import sys

old_version = sys.argv[1]
new_version = sys.argv[2]
path = Path("pyproject.toml")
content = path.read_text()
old = f'version = "{old_version}"'
new = f'version = "{new_version}"'

if old not in content:
    raise SystemExit("Error: version string not found in pyproject.toml")

path.write_text(content.replace(old, new, 1))
PY

echo "Building package..."
python -m build
echo "Build status: success"

echo "Uploading package..."
twine upload dist/*
echo "Upload status: success"
