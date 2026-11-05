---
name: deep-module-design
description: Use when designing, reviewing, or reshaping a module, interface, API, package, or seam; when deciding where logic belongs, how to make code more testable, or how to reduce coupling; when simplifying behavior-preserving code; or when planning a deprecation or migration.
---

# Deep Module Design

## Environment

Invoked directly by a human or by an agent mid-task; there may be no agent file.
Read the repository's instructions (`AGENTS.md`, `CONTRIBUTING`, `README`) and
the code before proposing a design. If a required operation is undefined and
would change shared state, ask; otherwise use your judgment.

## Overview

Design **deep modules**: a lot of behavior behind a small interface, at a clean
seam, testable through that interface. The aim is leverage for callers, locality
for maintainers, and testability for everyone.

Use these terms exactly. They are the shared vocabulary:

| Term | Meaning |
|---|---|
| **Module** | Anything with an interface and an implementation: function, class, package, or slice. |
| **Interface** | Everything a caller must know: types, invariants, ordering, error modes, configuration, performance. |
| **Implementation** | The body of code inside a module. |
| **Depth** | Behavior a caller can exercise per unit of interface they must learn. |
| **Seam** | The place where a module's interface lives and behavior can change without editing there. |
| **Adapter** | A concrete thing that satisfies an interface at a seam. |
| **Leverage** | What callers get from depth: more capability per unit of interface. |
| **Locality** | What maintainers get from depth: change and verification concentrate in one place. |

## Process

### 1. Define the module and its callers

Write one sentence for what the module is responsible for. List its callers and
the tests that cross the seam. If the responsibility needs "and", it is probably
two modules.

Before naming the interface, run the deletion test: imagine deleting the module.
If the complexity vanishes, it was a pass-through; merge it into its caller or
stop. If the complexity reappears across callers, it earns its keep. Record the
result in one line.

### 2. Name the interface

List everything a caller must know: signatures, invariants, ordering, error
modes, required configuration, and performance characteristics. The type
signature is only part of it.

Prefer an interface that is hard to misuse: fewer methods, simpler parameters,
explicit result types, and no leaked implementation detail.

A production interface carries production capabilities only. Do not add a
method that only tests call; seed through a test builder, an internal fixture,
or `InternalsVisibleTo`.

### 3. Place the seam

Prefer an existing seam. Put a new seam as high as practical, where callers
already interact. One adapter means a hypothetical seam; two adapters mean a
real one. Do not introduce a seam unless something actually varies across it.

### 4. Test the depth

Apply these tests before writing the implementation:

- **Test surface.** Callers and tests cross the same interface. If a test must
  reach past it, the module is the wrong shape.
- **Dependency direction.** Accept dependencies; do not create them inside.
  Return results; do not mutate the caller.
- **Shallowness check.** If the interface is nearly as complex as the
  implementation, either deepen the module or merge it into its caller.

### 5. Design it twice

Sketch two or three radically different interfaces for the same responsibility.
Compare them on depth, locality, seam placement, and testability. Pick one and
state why the others lost. This is cheaper than discovering the shallow version
during implementation.

### 6. Name the domain

Use the project's glossary terms in the interface. If a concept lacks a name,
name it once and record it. When the decision would be expensive to reverse,
trigger an ADR and use `documentation` for its format.

### 7. Simplify without changing behavior

Before removing anything, answer Chesterton's fence: what is this responsible
for, who calls it, what are its edge cases, and why might it have been written
this way? Check the history.

Then make one behavior-preserving change at a time, run the tests, and keep
refactoring separate from feature work. The goal is comprehension speed, not line
count. Scope the work to the module in question; do not renovate neighbors.

### 8. Migrate in reversible steps

- Build and prove the replacement before deprecating anything.
- Prefer advisory deprecation; use a compulsory deadline only when maintenance or
  security cost justifies it.
- Use an adapter, a feature flag, or the strangler pattern to move consumers
  incrementally.
- For a schema or shared-shape change, use expand, migrate, contract: add the new
  form beside the old, backfill, switch reads, then remove the old form in a
  separate deploy.
- Every migration needs a tested down path, or a restorable backup plus an
  approved one-way decision, and a way to verify zero remaining consumers.

## Verification

- [ ] The module has one stated responsibility and one interface.
- [ ] The interface lists invariants, errors, ordering, and configuration, not
      just types.
- [ ] The seam is at an existing caller boundary, and something actually varies
      across it.
- [ ] The deletion test and the test-surface test pass.
- [ ] At least two alternative interfaces were compared.
- [ ] Domain terms are used consistently, or the gap is recorded.
- [ ] Simplification preserves behavior and keeps tests unchanged.
- [ ] A migration has a proven replacement, a down path or approved backup, and
      a zero-consumer check before removal.
