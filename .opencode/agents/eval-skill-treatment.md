---
description: Treatment arm for the skill-forge stop-rule test; skill-forge allowed, pinned default model
mode: subagent
model: opencode-go/deepseek-v4.1-flash
permissions:
  - action: skill
    resource: "*"
    effect: deny
  - action: skill
    resource: "skill-forge"
    effect: allow
  - action: subagent
    resource: "*"
    effect: deny
---

You are an evaluation treatment. Work only on the task in the prompt.
