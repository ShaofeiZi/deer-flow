---
name: translation
description: One-click translation of English comments and logs in a directory into Chinese while keeping the original English (bilingual, preserving technical terms), with parallel/serial execution and quality validation. Use when the user says "translation", "translate comments", "translate logs", "comment translation", or similar.
---

# translation - One-Click Translation of Code Comments and Logs (Bilingual)

An engineering-oriented "one-click translation" skill: by default it runs **Scan → Translate → Quality Validation → Report** directly against the target directory, and strives to:

- Only modify human-readable text in comments and logs, never code semantics
- **Translate into Chinese while keeping the corresponding original English (bilingual)**
- Preserve common technical terms in English (e.g., API/HTTP/JSON)
- Roll back to a backup and flag the issue in the report when grammar/quality problems occur

## Usage

```bash
/translation [target-directory-path] [--mode=swarm|serial]
```

- `target-directory-path`: Optional. Defaults to the current working directory (command execution path).
- `--mode`: Optional. Defaults to `swarm` (parallel); `serial` (sequential) is also available.

Examples:

```bash
/translation
/translation /path/to/project/src
/translation /path/to/project --mode=serial
```

## Default Behavior (Contract)

### Translation Scope

- Translation targets: natural-language text in code comments (single-line / multi-line / doc comments) and log statements.
- **Bilingual preservation**: the original English **must be kept** after translation, never dropped. Specific rules:
  - Multi-line / block comments: append the Chinese translation below the English original (or vice versa); both coexist.
  - Single-line comments: use the form `original English | Chinese translation`, or add a separate Chinese comment line above, ensuring the English is not removed.
  - Log strings: by default keep English only (to avoid breaking log search and alert matching); if Chinese is truly required, append it as `English text (中文)` and never replace the original English.
- Kept unchanged: identifiers, function names, class names, paths, URLs, regex, formatting placeholders (e.g., `%s`, `{name}`), code snippets, and indentation layout.
- Technical terms: kept in English by default (the glossary can be extended in the session).

### Skipped by Default (avoid accidental edits and noise)

The following directory/file patterns are not processed by default (adjustable in the session):

- Directories: `node_modules/`, `dist/`, `build/`, `vendor/`, `coverage/`, `.git/`
- Files: `**/*.min.*`, large files (e.g., > 1MB), and obvious generated files (e.g., `generated/`, `__generated__/`)

### Output and Traceability

Each run creates (or reuses) a working directory under the target directory: `<target-directory>/.translation/`

Minimal output set:

- Session state: `<target-directory>/.translation/sessions/<session-id>.md`
- Execution log: `<target-directory>/.translation/logs/<session-id>.log`
- Original file backups: `<target-directory>/.translation/backup/<session-id>/...`

## Subtask Delegation Mechanism (DeerFlow)

> Important: this skill runs inside DeerFlow, which has **no `.md`-based sub-agent files**, and you cannot reference a sub-agent via a `file:///` link.
> DeerFlow delegates subtasks through the built-in `task` tool; the available `subagent_type` values are `general-purpose` and `bash`.
> Note: sub-agents have the `task` tool disabled by default (they cannot delegate further), so **the main agent that activates this skill acts as the coordinator**.
> The main agent is responsible for splitting the work list and launching subtasks; sub-agents must not call each other.

Invocation (illustrative):

```text
task(
  subagent_type="general-purpose",
  description="translate file batch",
  prompt="<explicit translation scope, bilingual rules, target file list, backup and write-back requirements>"
)
```

## One-Click Workflow

### swarm (default, parallel)

1. **Coordination (main agent)**: initialize the session and state files (`<target-directory>/.translation/`).
2. **Scan**: the main agent uses `Glob`/`Grep` or a single `general-purpose` subtask to produce the to-be-translated list (file list, comment/log statistics, priorities, recommended batch granularity).
3. **Translate (parallel subtasks)**: the main agent splits the list into batches and launches multiple `task(subagent_type="general-purpose")` **in parallel**, each handling one batch of files:
   - Copy original files into `backup/<session-id>/` before writing back.
   - Strictly enforce the "bilingual preservation" rules; only modify comment/log text.
4. **Quality validation**: after all translations complete, the main agent launches a `general-purpose` subtask (or does it itself) to run: integrity check (is the English preserved), terminology consistency, and syntax/parseability check (a `bash` subtask can run lint/compile/syntax parsing), producing a quality conclusion.
5. **Aggregate report**: the main agent aggregates the success / failure / manual-handling lists, along with output paths and rollback notes.

### serial (sequential)

Same scan/translate/validate steps as swarm, but subtasks are launched **file by file sequentially**, suitable for small projects or stronger context-consistency requirements.

## Failure and Rollback (Key Guarantee)

When any of the following conditions is met, the file should be marked as failed and rolled back from `backup/<session-id>/` (or at least explicitly flagged in the report):

- Obvious syntax errors appear after translation, or the file cannot be parsed/compiled.
- **The original English is removed** (violating the bilingual preservation rules).
- Key technical terms are mistranslated in a way that harms comprehension.
- Quality validation fails (the specific threshold is determined by the validation-step policy).

## Execution Rules

- **No semantic changes**: only modify natural-language text in comments and logs; never alter code logic, identifiers, or placeholders.
- **Always keep English**: never delete the original English under any circumstances, to preserve traceability and keep log search intact.
- **Back up before writing back**: before writing back any file, it must first be backed up to `backup/<session-id>/`.
- **Idempotent**: repeated runs must not stack duplicate translations; skip lines that already contain a Chinese translation.
- **Respect delegation constraints**: only the main agent launches `task`; sub-agents do not delegate further.
