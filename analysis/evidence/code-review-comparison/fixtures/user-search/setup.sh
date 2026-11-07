#!/usr/bin/env bash
# Build a review repository: main has the profile endpoint, feature/user-search
# adds the search endpoint and its spec.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="${1:?usage: $0 <destination> [seeded|clean]}"
mode="${2:-seeded}"

rm -rf "$dest"
mkdir -p "$dest"
cp -R "$script_dir/main/." "$dest/"

cd "$dest"
git init -q -b main
git config user.email dev@example.com
git config user.name Dev
git add -A
git commit -qm "feat: user profile endpoint"
git checkout -qb feature/user-search

cp -R "$script_dir/feature/." "$dest/"
if [ "$mode" = "clean" ]; then
  cp -R "$script_dir/clean/." "$dest/"
fi
git add -A
git commit -qm "feat: add user search endpoint"

echo "repository ready at $dest"
