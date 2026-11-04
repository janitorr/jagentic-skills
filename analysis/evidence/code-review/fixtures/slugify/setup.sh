#!/usr/bin/env bash
# Build a code-review fixture from the vertical-slice-tdd template.
#
#   main                  stub slugify, baseline commit
#   feature/add-slugify   implemented slugify, tests green, tasks checked
#
# With SEED=1 the feature branch also narrows the whitespace regex from \s+ to
# " +": the suite still passes, and the spec's "whitespace runs" clause is
# violated for tabs and newlines.
#
# Usage: ./setup.sh [destination] [seed]
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
dest=${1:-/tmp/opencode/code-review-fixture}
seed=${2:-0}

rm -rf "$dest"
cp -r "$repo/analysis/evidence/vertical-slice-tdd/fixtures/template" "$dest"
cd "$dest"

git init -q -b main
git add .
git -c user.email=eval@local -c user.name=eval commit -q -m "fixture baseline"

git checkout -q -b feature/add-slugify
cp "$here/clean/src/text.py" src/text.py
cp "$here/clean/tests/test_text.py" tests/test_text.py
cp "$here/clean/tasks.md" openspec/changes/add-slugify/tasks.md
git add .
git -c user.email=eval@local -c user.name=eval commit -q -m "feat: implement slugify"

if [ "$seed" = "1" ]; then
  sed -i 's/re.sub(r"\\s+"/re.sub(r" +"/' src/text.py
  git -c user.email=eval@local -c user.name=eval commit -q -am "feat: collapse repeated spaces"
fi

echo "built $dest (seed=$seed)"
echo "review: feature/add-slugify against main"
