#!/usr/bin/env bash
# Build a review fixture: main has the baseline, feature/user-search adds the
# search endpoint and its spec.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="${1:?usage: $0 <destination> [seeded|clean]}"
mode="${2:-seeded}"

rm -rf "$dest"
mkdir -p "$dest"
cp -R "$script_dir/main/." "$dest/"

cd "$dest"
git init -q -b main
git config user.email eval@example.com
git config user.name eval
git add -A
git commit -qm "baseline: user profile endpoint"
git checkout -qb feature/user-search

cp -R "$script_dir/feature/." "$dest/"
if [ "$mode" = "clean" ]; then
  cp -R "$script_dir/clean/." "$dest/"
fi
git add -A
git commit -qm "add user search endpoint"

echo "fixture ready at $dest"
