---
name: load
description: Scan the current folder, repository, or codebase for factual context before further work. Use when the user asks to load, scan, inspect, understand, or get context for the current project, especially when they want the agent to gather facts first and then wait for instructions.
---

# Load

Scan only for facts that are relevant to the user's stated focus, then stop and await further instructions.

## Workflow

1. Identify the user's requested focus.
2. If the focus is specific, inspect only the relevant project areas.
3. If the focus is absent or too broad, run a generic scan.
4. Report facts only.
5. State that context is loaded and wait for the user's next instruction.

## Relevant Scan

When the user gives a focus, choose commands and files that directly support that focus. Prefer fast, read-only inspection such as:

- `pwd`
- `ls`
- `find`
- `rg --files`
- `rg`
- `git status`
- `git branch`
- `git log`
- manifest or config reads
- source and test file reads

Do not inspect unrelated parts of the project unless needed to understand the requested focus.

## Generic Scan

When the user gives no specific focus, inspect:

- current path
- top-level folder structure
- git branch and working tree status
- recent git history
- dependency manifests
- build, test, lint, and runtime config
- README and project documentation
- source entry points
- test layout
- CI or deployment config

## Output

Keep the response factual and at most 200 words.

Include:

- concise repo briefing
- exact files, folders, commands, or facts discovered when useful
- a final sentence that context is loaded and the agent is waiting for further instructions

## Constraints

Do not guess.

Do not suggest next steps.

Do not recommend changes.

Do not propose plans.

Do not make assumptions beyond observed facts.

Do not edit files, run tests, install dependencies, or start services unless the user explicitly asks after the scan.
