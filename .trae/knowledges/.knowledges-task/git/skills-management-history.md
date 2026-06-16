## 6dce26a5 2026-04-20 Ansel
fix: resolve tool duplication and skill parser YAML inconsistencies (#1803) (#2107)

* Refactor tests for SKILL.md parser

Updated tests for SKILL.md parser to handle quoted names and descriptions correctly. Added new tests for parsing plain and single-quoted names, and ensured multi-line descriptions are processed properly.

* Implement tool name validation and deduplication

Add tool name mismatch warning and deduplication logic

* Refactor skill file parsing and error handling

* Add tests for tool name deduplication

Added tests for tool name deduplication in get_available_tools(). Ensured that duplicates are not returned, the first occurrence is kept, and warnings are logged for skipped duplicates.

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* Update minimal config to include tools list

* Update test for nonexistent skill file

Ensure the test for nonexistent files checks for None.

* Refactor tool loading and add skill management support

Refactor tool loading logic to include skill management tools based on configuration and clean up comments.

* Enhance code comments for tool loading logic

Added comments to clarify the purpose of various code sections related to tool loading and configuration.

* Fix assertion for duplicate tool name warning

* Fix indentation issues in tools.py

* Fix the lint error of test_tool_deduplication

* Fix the lint error of tools.py

* Fix the lint error

* Fix the lint error

* make format

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/skills/parser.py`
  L13: """Parse a SKILL.md file and extract metadata.
  L30: # Extract YAML front-matter block between leading ``---`` fences.
  L47: # Extract required fields.  Both must be non-empty strings.
  L56: # Normalise: strip surrounding whitespace that YAML may preserve.

## 11f557a2 2026-04-24 Airene Fang
feat(trace):Add run_name to the trace info for system agents. (#2492)

* feat(trace): Add `run_name` to the trace info for suggestions and memory.

before(in langsmith):
CodexChatModel
CodexChatModel
lead_agent
after:
suggest_agent
memory_agent
lead_agent

feat(trace): Add `run_name` to the trace info for suggestions and memory.

before(in langsmith):
CodexChatModel
CodexChatModel
lead_agent
after:
suggest_agent
memory_agent
lead_agent

* feat(trace): Add `run_name` to the trace info for system agents.

before(in langsmith):
CodexChatModel
CodexChatModel
CodexChatModel
CodexChatModel
lead_agent
after:
suggest_agent
title_agent
security_agent
memory_agent
lead_agent

* chore(code format):code format

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/skills/security_scanner.py`

## 707ed328 2026-04-28 DanielWalnut
fix(skills): scan skill archives before install (#2561)

* fix(skills): scan skill archives before install

Fixes #2536

* fix(skills): scan archive support files before install

* style(skills): format archive installer

* fix(skills): address archive install review comments

- `backend/packages/harness/deerflow/skills/__init__.py`
- `backend/packages/harness/deerflow/skills/installer.py`
  L32: """Raised when a skill archive fails security scanning."""
  L179: """Run the skill security scanner against all installable text and script files."""
  L289: """Install a skill from a .skill archive (ZIP)."""

## e82940c0 2026-04-28 greatmengqi
refactor: thread release config through lead path (#2612)

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/packages/harness/deerflow/skills/loader.py`
- `backend/packages/harness/deerflow/skills/manager.py`
- `backend/packages/harness/deerflow/skills/security_scanner.py`

## 1ad1420e 2026-05-01 Xun
refactor(skills): Unified skill storage capability (#2613)

- `backend/packages/harness/deerflow/skills/__init__.py`
- `backend/packages/harness/deerflow/skills/installer.py`
- `backend/packages/harness/deerflow/skills/parser.py`
- `backend/packages/harness/deerflow/skills/security_scanner.py`
- `backend/packages/harness/deerflow/skills/storage/__init__.py`
  L1: """SkillStorage singleton + reflection-based factory.
  L4: """
  L16: """Return a ``SkillStorage`` instance — either a new one or the process singleton.
  L27: """
  L49: # No app_config: use a default SkillsConfig so we never need to read config.yaml
  L50: # when the caller has already supplied an explicit host path.
  L58: # If the singleton was manually injected (e.g. in tests) without a config
  L59: # identity (_default_skill_storage_config is None), skip get_app_config()
  L60: # entirely to avoid requiring a config.yaml on disk.
  L72: """Clear the cached singleton (used in tests and hot-reload scenarios)."""
- `backend/packages/harness/deerflow/skills/storage/local_skill_storage.py`
  L1: """Local-filesystem implementation of ``SkillStorage``."""
  L25: """Skill storage backed by the local filesystem.
  L32: """
  L52: # ------------------------------------------------------------------
  L53: # Abstract operation implementations
  L54: # ------------------------------------------------------------------
- `backend/packages/harness/deerflow/skills/storage/skill_storage.py`
  L1: """Abstract SkillStorage base class with template-method flows."""
  L19: """Abstract base for skill storage backends.
  L25: """
  L30: # ------------------------------------------------------------------
  L31: # Static protocol helpers (not storage-specific)
  L32: # ------------------------------------------------------------------
  L36: """Validate and normalise a skill name; return the normalised form."""
  L46: """Validate *relative_path* against *base_dir* and return the resolved target.
  L51: """
  L64: """Validate SKILL.md content: parse frontmatter and check name matches."""
  L80: """Validate and return the resolved absolute path for a support file."""
  L101: # ------------------------------------------------------------------
  L102: # Abstract atomic operations (storage-medium specific)
  L103: # ------------------------------------------------------------------
  L107: """Absolute host path to the skills root, used for sandbox mounts.
  L110: """
  L114: """Yield ``(category, category_root, skill_md_path)`` for every SKILL.md.
  L118: """
  L122: """Read SKILL.md content for a custom skill.
  L125: """
  ... (truncated)
- `backend/packages/harness/deerflow/skills/types.py`
  L9: """Source category for a skill.
  L13: """
- `backend/packages/harness/deerflow/skills/validation.py`

## c09c3345 2026-05-01 Nan Gao
fix(harness): resolve runtime paths from project root (#2642)

* fix(harness): resolve runtime paths from project root

* docs(config): update

* fix(config): address runtime path review feedback

* test(config): fix skills path e2e root

* test(config): cover legacy config fallback when project root lacks config files

Verifies that when DEER_FLOW_PROJECT_ROOT is unset and cwd has no
config.yaml/extensions_config.json, AppConfig and ExtensionsConfig fall back
to the legacy backend/repo-root candidates — the backward-compat path
requested in PR #2642 review.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/skills/storage/local_skill_storage.py`

## cef42243 2026-05-07 AochenShen99
fix(skills): enforce allowed-tools metadata (#2626)

* fix(skills): parse allowed-tools frontmatter

* fix(skills): validate allowed-tools metadata

* fix(skills): add shared allowed-tools policy

* fix(subagents): enforce skill allowed-tools

* fix(agent): enforce skill allowed-tools

* refactor(skills): dedupe TypeVar and reuse cached enabled skills

- Drop redundant module-level TypeVar in tool_policy; rely on PEP 695 syntax.
- Expose get_cached_enabled_skills() and have the lead agent reuse it
  instead of synchronously rescanning skills on every request.

* fix(agent): expose config-scoped skill cache

* fix(subagents): pass filtered tools explicitly

* fix(skills): clean allowed-tools policy feedback

- `backend/packages/harness/deerflow/skills/parser.py`
  L13: """Parse the optional allowed-tools frontmatter field.
  L18: """
- `backend/packages/harness/deerflow/skills/tool_policy.py`
  L14: """Return the union of explicit skill allowed-tools declarations.
  L20: """
- `backend/packages/harness/deerflow/skills/types.py`
- `backend/packages/harness/deerflow/skills/validation.py`

## a814ab50 2026-05-17 Willem Jiang
fix(skills): make security scanner JSON parsing robust for LLM output variations (#2987)

The moderation model's response was silently falling through to a
  conservative block when LLMs wrapped structured output in markdown
  code fences, added prose around the JSON, returned case-variant
  decisions (e.g. "Allow"), or included nested braces in the reason
  field. The greedy `\{.*\}` regex also over-matched on nested braces.

  - Rewrite _extract_json_object() with markdown fence stripping and
    brace-balanced string-aware extraction
  - Normalize decision field to lowercase for case-insensitive matching
  - Distinguish "model unavailable" from "unparseable output" in fallback
  - Strengthen system prompt to explicitly forbid code fences and prose
  - Add 15 tests covering all reported scenarios

  Fixes #2985

- `backend/packages/harness/deerflow/skills/security_scanner.py`
  L27: # Strip markdown code fences (```json ... ``` or ``` ... ```)
  L37: # Brace-balanced extraction with string-awareness

## 8decfd32 2026-05-28 AochenShen99
Fix custom skill install permissions (#3241)

* Fix custom skill install permissions

* Fix skill upload test portability

* Keep custom skill writes sandbox readable

* Clear sandbox write bits on skill permissions

* Limit custom skill write permission updates

- `backend/packages/harness/deerflow/skills/installer.py`
- `backend/packages/harness/deerflow/skills/permissions.py`
  L1: """Filesystem permission helpers for installed skill trees."""
- `backend/packages/harness/deerflow/skills/storage/local_skill_storage.py`

## 89ae74d4 2026-06-03 Huixin615
fix(skills): surface offending line and quoting hint on SKILL.md YAML… (#3335)

* fix(skills): surface offending line and quoting hint on SKILL.md YAML errors

When a SKILL.md front-matter fails to parse, the existing log only
echoes PyYAML's raw message, leaving authors to grep the file for the
offending line. This is especially painful for the very common
LLM-authored mistake of an unquoted scalar containing ': '
(e.g. 'description: foo: bar'), which fails with
'mapping values are not allowed here' and silently drops the skill.

Enrich the error log with:
  - the source line PyYAML pointed at via problem_mark
  - a targeted, copy-pasteable quoting hint when (and only when) the
    error is the well-known 'mapping values are not allowed' scanner
    error on an unquoted value

The skill is still rejected (no semantics are guessed or rewritten);
only the diagnostic is improved.

Fixes #3333

* improve(skills): address CR feedback on SKILL.md YAML error diagnostics

Per review on #3335:

- Log the file line number (mark.line + 2) instead of the
  front-matter-internal line number, so authors land on the right
  row in their editor.
- Use exc.problem == "mapping values are not allowed here" for a
  tighter match than substring-scanning str(exc).
- Preserve the offending key's leading whitespace in the quoting
  hint so nested mappings stay nested when authors paste the fix
  back.
- Rewrite the regression test to actually exercise the new
  behaviour: PyYAML's own message already echoes the offending
  line (and truncates it with "..."), so the old assertion
  passed on main. New assertions pin (a) the file-line number,
  (b) the full untruncated line, and (c) the copy-pasteable hint.
- Add a guard test for nested-key indentation so the
  partition()/strip() shape cannot regress silently.

Refs #3333, #3335

* fix(skills): escape backslashes in YAML quoting hint

The hint emitted by _format_yaml_error previously escaped only double
quotes, so values containing backslashes (e.g. Windows paths like
C:\Temp or regex escapes like \d) produced a suggested scalar that
was either invalid YAML or silently re-interpreted by PyYAML's
double-quoted escape rules when pasted back. Escape order matters:
backslashes first, then double quotes.

Adds two regression tests covering Windows-path and regex-style
backslashes.

Address Copilot CR feedback on PR #3335.

- `backend/packages/harness/deerflow/skills/parser.py`
  L13: """Render a developer-friendly explanation of a YAML front-matter error."""
  L22: # mark.line is 0-based within the front-matter body; +1 makes it
  L23: # 1-based, +1 more accounts for the leading `---` fence that the
  L24: # front-matter regex strips before yaml.safe_load sees it. The
  L25: # result matches the line number an author sees in their editor.
  L29: # Targeted hint for the most common authoring mistake: an unquoted
  L30: # scalar value whose body contains ``: ``. We only surface the hint
  L31: # when we are confident it applies, to avoid misleading authors who
  L32: # hit unrelated YAML errors.

## 16391e35 2026-06-09 DanielWalnut
fix(skills): harden slash skill activation across chat channels (#3466)

* support slash skill activation

* format slash skill activation

* Preserve slash skill activation with uploads

* Address slash skill review feedback

* Address slash skill follow-up review

* Fix lazy slash skill storage resolution

* Keep slash skill activation out of system prompt

* Address slash skill review issues

* fix: harden slash skill command handling

* feat(frontend): add slash skill autocomplete

* fix: address slash skill review feedback

* fix: preserve slash skill text for IM uploads

- `backend/packages/harness/deerflow/skills/slash.py`
  L14: """Parsed slash-skill command with the skill name and remaining task text."""
  L22: """Slash-skill activation resolved against enabled runtime-visible skills."""
  L30: """Parse strict `/skill-name task` syntax, ignoring reserved control commands."""
  L50: """Resolve text into an enabled, whitelisted skill activation if possible."""

