# Agent Instructions

This file defines how AI agents (Claude, GPT, etc.) should work on this project.

---

## Getting Started

-   Read **[`README.md`](README.md)** for project overview
-   Check **[`package.json`](package.json)** for available npm commands
-   Review **[`.github/instructions/`](.github/instructions/)** for coding conventions
-   Review **[`docs/`](docs/)** for architecture and setup details
-   Look at similar modules/files and follow existing patterns

> **If you are a Claude agent** (for example, `claude-4.5-sonnet`) - other agents ignore:
> Check **[`.claude/rules/`](.claude/rules/)** for specialized instructions (automatically loaded into memory)
> Ignore **[`.github/instructions/`](.github/instructions/)** as it contains the same files as `.claude/rules/`
> Never modify files in `.claude/rules/` and `.claude/commands/`

---

## Planning

For non-trivial tasks, write a plan before coding:

1. Create a plan file in `docs/plans/` using format `YYYY-MM-DD-feature-name.md`
2. Include: goal, approach, files to modify, and implementation steps
3. Get user approval before executing
4. Update the plan if the approach changes significantly

---

## What NOT to Do

Unless explicitly requested:

❌ **Tests** – Never generate, update, or modify test files.
❌ **Dependencies** – Never upgrade frameworks, libraries, or dependencies.
❌ **Scope** – Never add features beyond the request's scope.
❌ **Compatibility** – Never maintain backward compatibility unless specified.
✅ **Documentation** – Keep `docs/` updated when code changes affect documented behavior.
❌ **Protected Files** – Never modify these read-only files:
`AGENTS.md`, `CLAUDE.md`, `.github/instructions/`, `.github/prompts/`, `.claude/commands/`, `.claude/rules/`, `docs/architecture/protected-files.md`

---

## Communication

### Response Format

-   Be concise, minimize prose.
-   Say **"I don't know"** rather than guess.
-   Confirm understanding **before coding** when requirements are ambiguous.
-   Be explicit about what changes you're making.

### For Code Changes

```text
I'll [brief action description].

Changes made:
- [Specific change 1] in [file path]
- [Specific change 2] in [file path]
```

### For Errors

```text
Issue: [Problem statement]
Solution: [Proposed fix]
```

---

## Development Process

### File Structure

-   Add file path at top of each file:
    `// src/modules/example.js - Module for handling user authentication`
-   Add a 1-line function description as a comment above each function:
    `// Extract JWT token from request based on endpoint type`
-   Keep related code together in a logical hierarchy.
-   No obvious comments, no commented-out code. Code should be self-documenting; if a comment explains _what_, refactor instead.

### Code Quality

-   Plan step-by-step in detailed pseudocode **before** coding.
-   Write correct, functional, secure, and efficient code.
-   Prioritize readability over performance.
-   Include all imports and proper component naming.
-   No todos, placeholders, or missing pieces.
-   Do not create redundant code; extend the existing codebase.

### Single Responsibility Principle

-   Each function should do exactly one thing.
-   Functions should be small and focused.
-   If a function needs **multiple comments** to explain different steps, split it.

---

## Documentation Structure

> Only `CLAUDE.md`, `AGENTS.md`, and `README.md` are allowed in the repository root.

### Reference Docs

| File                             | Purpose                                  |
| -------------------------------- | ---------------------------------------- |
| [`README.md`](README.md)         | Project context, tech stack, quick-start |
| [`docs/setup.md`](docs/setup.md) | Installation, configuration              |
| [`docs/codebase.md`](docs/codebase.md) | Directory structure, file descriptions   |

### Historical Records (Not Feature Documentation)

> ⚠️ **Do not use these for understanding existing features.** They are incomplete historical records.

-   **[`docs/plans/`](docs/plans/)** – Past implementation plans (format: `YYYY-MM-DD-feature-name.md`)
-   **[`docs/changelog/`](docs/changelog/)** – Past change notes

### Changelog Maintenance

After significant changes (new features, refactoring, bug fixes, API changes, removals), prompt the user: "Would you like me to create a changelog entry for this?" If yes, create a detailed file in `docs/changelog/` and update `docs/changelog/CHANGELOG.md` with a summary entry. If changes span multiple commits, include: `Commits: abc1234, def5678, ghi9012`

### Missing Documentation

If a referenced `docs/*` file doesn't exist, create it matching the description above and the style of existing docs.
