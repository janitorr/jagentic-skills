#!/usr/bin/env bash
# Clone or fast-forward each bundle listed in bundles.txt.
# Format per line: <name> <git-url>   (# comments and blank lines ignored)
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p vendor

while read -r name url _; do
  [[ -z "${name:-}" || "$name" == \#* ]] && continue
  dest="vendor/$name"
  if [[ -d "$dest/.git" ]]; then
    echo "updating $name"
    git -C "$dest" fetch --quiet --all
    git -C "$dest" pull --quiet --ff-only
  else
    echo "cloning $name from $url"
    git clone --quiet --depth 1 "$url" "$dest"
  fi
done < bundles.txt
