---
description: Control arm for the skill-forge stop-rule test; no skills, pinned default model
mode: subagent
model: opencode-go/deepseek-v4.1-flash
permissions:
  - action: skill
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: deny
---

You are an evaluation control. Work only on the task in the prompt.
