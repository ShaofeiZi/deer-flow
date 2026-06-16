---
name: knowledge-backend-core-skills-management
description: >
  Covers skills management: Skill dataclass with SkillCategory enum, SKILL.md YAML
  frontmatter parser, skill archive installer with zip bomb protection and symlink
  rejection, skill storage with enable/disable, tool policy filtering by skill
  allowed-tools, and slash skill activation. Navigate when: adding skill installation
  features, modifying skill parsing, debugging skill loading, configuring skill
  security, or working on skill-based tool restrictions. This is a component-like
  module consumed by agent orchestration, tool ecosystem, and runtime engine.
  Excludes: skill content definitions (see skills/ in root), agent factory (see ../agent-orchestration/).
  Keywords: Skill, SkillCategory, SkillStorage, skill installer, skill parser,
  SKILL.md, YAML frontmatter, zip bomb protection, symlink rejection, allowed-tools,
  tool_policy, filter_tools_by_skill_allowed_tools, slash skill activation,
  SkillActivationMiddleware, skill_manage_tool.
---

## Module Structure

Skills management handles the lifecycle of agent skills: parsing SKILL.md metadata,
installing skill archives with security checks, storing and querying skills, and enforcing
tool access policies based on skill declarations.

### Directory Layout
- `backend/packages/harness/deerflow/skills/__init__.py` — Public API: Skill, storage, installer errors
- `backend/packages/harness/deerflow/skills/types.py` — Skill dataclass, SkillCategory enum, container path resolution
- `backend/packages/harness/deerflow/skills/parser.py` — SKILL.md YAML frontmatter parser with error formatting
- `backend/packages/harness/deerflow/skills/installer.py` — Skill archive extraction with security checks
- `backend/packages/harness/deerflow/skills/storage/` — Skill storage with enable/disable, querying
- `backend/packages/harness/deerflow/skills/tool_policy.py` — `filter_tools_by_skill_allowed_tools()`
- `backend/packages/harness/deerflow/skills/slash.py` — Slash skill reference parsing and resolution
- `backend/packages/harness/deerflow/agents/middlewares/skill_activation_middleware.py` — Slash skill activation middleware
- `backend/packages/harness/deerflow/tools/skill_manage_tool.py` — Skill management tool for agents

### Key Entry Points
- `Skill` dataclass in `backend/packages/harness/deerflow/skills/types.py` — Core skill data model
- `SkillStorage` in `backend/packages/harness/deerflow/skills/storage/` — Skill persistence and querying
- `parse_skill_md()` in `backend/packages/harness/deerflow/skills/parser.py` — SKILL.md parser
- `install_skill()` in `backend/packages/harness/deerflow/skills/installer.py` — Skill archive installer
- `filter_tools_by_skill_allowed_tools()` in `backend/packages/harness/deerflow/skills/tool_policy.py` — Tool restriction

## API Surface

### Skill (dataclass)
- `name` — Skill name (from SKILL.md frontmatter)
- `description` — Skill description
- `license` — Skill license type
- `skill_dir` — Local filesystem path to skill directory
- `category` — SkillCategory enum (PUBLIC or CUSTOM)
- `allowed_tools` — Optional list of tool names this skill is allowed to use
- `enabled` — Whether the skill is currently enabled
- `container_path` — Computed property: skill path as seen from inside sandbox

### SkillCategory (enum)
- `PUBLIC` — Built-in skill, not user-editable
- `CUSTOM` — User-installed or user-created skill, editable

### SkillStorage
- `load_skills(enabled_only)` — Load all skills, optionally filtered to enabled only
- `get_skill(name)` — Get a specific skill by name
- `enable_skill(name)` / `disable_skill(name)` — Toggle skill enabled state
- `install_skill(archive_path)` — Install a skill from archive

## Usage Examples

### Loading enabled skills
```python
from deerflow.skills.storage import get_or_new_skill_storage

storage = get_or_new_skill_storage()
skills = list(storage.load_skills(enabled_only=True))
```

### Filtering tools by skill policy
```python
from deerflow.skills.tool_policy import filter_tools_by_skill_allowed_tools

filtered_tools = filter_tools_by_skill_allowed_tools(raw_tools, enabled_skills)
```

## Gotchas
- Skill installer includes zip bomb protection — archives with excessive compression ratios are rejected (`backend/packages/harness/deerflow/skills/installer.py`)
- Symlinks in skill archives are rejected for security — only regular files and directories are extracted (`backend/packages/harness/deerflow/skills/installer.py`)
- Skill installer uses event-loop-aware dispatch for async installation — calling it from a sync context may require special handling (`backend/packages/harness/deerflow/skills/installer.py`)
- `filter_tools_by_skill_allowed_tools()` has a legacy allow-all behavior: if no skill declares `allowed-tools`, all tools are permitted (`backend/packages/harness/deerflow/skills/tool_policy.py`)
- Skill category determines mutability: PUBLIC skills show `[built-in]` label, CUSTOM skills show `[custom, editable]` label in prompts (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)

## Architecture
- Skill lifecycle: archive upload → security scan (zip bomb, symlinks) → extraction → SKILL.md parsing → storage registration → tool policy application (`backend/packages/harness/deerflow/skills/`)
- Skill storage is pluggable via config; default implementation uses filesystem-based storage with JSON metadata (`backend/packages/harness/deerflow/skills/storage/`)
- Tool policy filtering is applied at agent creation time: `get_available_tools()` → `filter_tools_by_skill_allowed_tools()` → agent receives restricted tool set (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Slash skill activation: user types `/skill-name` → SkillActivationMiddleware detects slash command → loads full SKILL.md content → injects as HumanMessage (`backend/packages/harness/deerflow/agents/middlewares/skill_activation_middleware.py`)

## Decisions
- Zip bomb protection was added to prevent denial-of-service via malicious skill archives (`backend/packages/harness/deerflow/skills/installer.py`)
- Symlink rejection was added to prevent path traversal attacks via skill archives (`backend/packages/harness/deerflow/skills/installer.py`)
- Legacy allow-all behavior for tool policy was preserved for backward compatibility — skills without `allowed-tools` don't restrict any tools (`backend/packages/harness/deerflow/skills/tool_policy.py`)
- Skill activation uses deterministic content hashing so retried activations replace rather than append content (`backend/packages/harness/deerflow/agents/middlewares/skill_activation_middleware.py`)

## Patterns
- Skill parser uses YAML frontmatter extraction with detailed error formatting including line numbers (`backend/packages/harness/deerflow/skills/parser.py`)
- Container path resolution: `skill.container_path` computes the path as seen from inside the sandbox (`/mnt/skills/<name>/`) (`backend/packages/harness/deerflow/skills/types.py`)
- Slash skill parsing: `parse_slash_skill_reference()` extracts skill name from user message, `resolve_slash_skill()` loads the skill content (`backend/packages/harness/deerflow/skills/slash.py`)

## Consumer Analysis
- Agent orchestration (agents/lead_agent/agent.py) — consumes `filter_tools_by_skill_allowed_tools()` and skill storage for tool policy and prompt injection
- Prompt template (agents/lead_agent/prompt.py) — consumes skill list for system prompt skills section
- Skill activation middleware (agents/middlewares/skill_activation_middleware.py) — consumes slash skill resolution
- Skill management tool (tools/skill_manage_tool.py) — consumes skill storage for agent-driven skill management
- Summarization middleware — consumes skill file read tool names for summarization preservation

## Conventions
- SKILL.md files use YAML frontmatter with `name`, `description`, `license`, `allowed-tools` fields (`backend/packages/harness/deerflow/skills/parser.py`)
- Skill directories are named after the skill and contain a `SKILL.md` file (`backend/packages/harness/deerflow/skills/types.py`)
- Container paths for skills use `/mnt/skills/` as the root prefix (`backend/packages/harness/deerflow/skills/types.py`)

## Dependencies
- PyYAML for SKILL.md frontmatter parsing (`backend/packages/harness/deerflow/skills/parser.py`)
- `deerflow.config.app_config` for skills configuration (container_path, storage) (`backend/packages/harness/deerflow/skills/`)
- LangChain for skill management tool definition (`backend/packages/harness/deerflow/tools/skill_manage_tool.py`)
