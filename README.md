# agentic-skills

A lab repo for comparing third-party agent skill bundles and synthesizing
new skills that combine the strongest ideas from each.

## Layout

```
vendor/     # upstream bundles, cloned (not tracked — see sync.sh)
analysis/   # category inventory, cross-bundle comparison, synthesis notes
skills/     # synthesized skills produced by the analysis
sync.sh     # clone/update every bundle listed in bundles.txt
bundles.txt # one "<name> <git-url>" per line
```

## Workflow

1. List bundles in `bundles.txt`.
2. `./sync.sh` — clone or fast-forward each bundle into `vendor/`.
3. Inventory skills into `analysis/inventory.md`, grouped by category.
4. Compare bundles per category in `analysis/comparison.md`.
5. Draft combined skills under `skills/<name>/SKILL.md`, with provenance
   notes pointing back to the source skills.
