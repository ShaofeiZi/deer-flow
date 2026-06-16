---
name: knowledge-skills-development
description: >
  Covers development and tooling skills: skill creation and evaluation, code
  documentation generation, agent identity bootstrapping, DeerFlow API interaction,
  skill discovery, Vercel deployment, and creative skill mashups.
  Navigate when: creating or improving skills, generating code docs, setting up
  agent identity, interacting with DeerFlow API, discovering installable skills,
  deploying to Vercel, or building creative skill combinations.
  Excludes: content creation (see ../content-creation/), data analysis (see
  ../data-analysis/), research (see ../research/).
  Keywords: skill-creator, code-documentation, bootstrap, SOUL.md, claude-to-deerflow,
  find-skills, vercel-deploy, surprise-me, eval, benchmark, init_skill, package_skill,
  DeerFlow, LangGraph, npx skills.
---

## Module Structure

Development skills provide meta-tooling for the skills ecosystem itself: creating and
evaluating skills, generating documentation, bootstrapping agent identity, interacting
with the DeerFlow platform, discovering community skills, deploying projects, and
creative skill orchestration.

### Directory Layout
- `skills/public/skill-creator/` — Meta-skill for skill lifecycle management
  - `scripts/init_skill.py` — New skill scaffolding
  - `scripts/package_skill.py` — Skill packaging into .skill file
  - `scripts/run_loop.py` — Description optimization loop
  - `scripts/run_eval.py` — Skill evaluation runner
  - `scripts/quick_validate.py` — Frontmatter validation
  - `scripts/aggregate_benchmark.py` — Benchmark aggregation
  - `scripts/generate_report.py` — Report generation
  - `scripts/improve_description.py` — Description improvement
  - `scripts/utils.py` — Shared utilities
  - `eval-viewer/generate_review.py` — HTML eval review viewer
  - `eval-viewer/viewer.html` — Viewer template
  - `agents/analyzer.md` — Benchmark analysis agent
  - `agents/comparator.md` — Blind A/B comparison agent
  - `agents/grader.md` — Assertion evaluation agent
  - `references/schemas.md` — JSON schemas for evals/grading
  - `references/output-patterns.md` — Output format patterns
  - `references/workflows.md` — Workflow documentation
- `skills/public/code-documentation/` — API/README/architecture doc generation
- `skills/public/bootstrap/` — Conversational SOUL.md onboarding
  - `templates/SOUL.template.md` — Output template
  - `references/conversation-guide.md` — Conversation strategies
- `skills/public/claude-to-deerflow/` — DeerFlow HTTP API client
  - `scripts/chat.sh` — Streaming chat helper
  - `scripts/status.sh` — Health check helper
- `skills/public/find-skills/` — Community skill discovery
  - `scripts/install-skill.sh` — Skill installation script
- `skills/public/vercel-deploy-claimable/` — Vercel deployment
  - `scripts/deploy.sh` — Deployment script
- `skills/public/surprise-me/` — Creative skill mashup generator

### Key Entry Points
- `init_skill.py` — Scaffold a new skill directory with SKILL.md template
- `package_skill.py` — Package a skill into a distributable .skill file
- `run_loop.py` — Automated description optimization (5 iterations, 60/40 train/test split)
- `chat.sh` — Send a message to DeerFlow and stream the response
- `deploy.sh` — Deploy a project directory to Vercel
- `install-skill.sh` — Install a community skill from owner/repo@name

## Gotchas
- Skill-creator eval grading.json MUST use fields `text`, `passed`, `evidence` — using `name`/`met`/`details` or other variants breaks the viewer (`skills/public/skill-creator/SKILL.md`, `skills/public/skill-creator/references/schemas.md`)
- Bootstrap's final SOUL.md must always be written in English regardless of the user's conversation language — this is a hard rule in the generation step (`skills/public/bootstrap/SKILL.md`)
- Bootstrap must call the `setup_agent` tool to persist SOUL.md — writing the file manually with bash tools is forbidden; if `setup_agent` returns an error, do not claim success (`skills/public/bootstrap/SKILL.md`)
- Skill-creator description optimization (`run_loop.py`) requires the `claude` CLI tool (`claude -p`) which is only available in Claude Code — skip this step on Claude.ai (`skills/public/skill-creator/SKILL.md`)
- Vercel deploy excludes `node_modules` and `.git` from the deployment tarball automatically — large binaries in other directories will still be included and may cause deployment failures (`skills/public/vercel-deploy-claimable/scripts/deploy.sh`)
- Skill-creator eval viewer must be generated BEFORE evaluating inputs yourself — the human review step is mandatory before making corrections (`skills/public/skill-creator/SKILL.md`)
- Code-documentation must analyze actual code before writing docs — never guess at API signatures or behavior; every code example must work with the described API (`skills/public/code-documentation/SKILL.md`)
- Find-skills installs skills globally to `skills/custom/` — not to `skills/public/` which is reserved for bundled skills (`skills/public/find-skills/SKILL.md`)

## Architecture
- Skill-creator is the central meta-skill with a full eval pipeline: draft → test (with-skill + baseline subagents) → grade (assertion evaluation) → aggregate (benchmark.json) → review (HTML viewer) → improve → repeat (`skills/public/skill-creator/SKILL.md`)
- Skill-creator uses a three-level loading system for skills: metadata (name + description, ~100 words) → SKILL.md body (<500 lines) → bundled resources (scripts, references, templates, assets loaded on demand) (`skills/public/skill-creator/SKILL.md`)
- DeerFlow exposes two API surfaces behind Nginx: Gateway API (REST: models, skills, memory, uploads) and LangGraph-compatible API (threads, runs, streaming) — both on port 8001 internally, proxied through port 2026 (`skills/public/claude-to-deerflow/SKILL.md`)
- Bootstrap follows a 4-phase conversational flow: Hello (language + first impression) → You (identity, role, pain points) → Personality (AI behavior, communication style, autonomy) → Depth (aspirations, blind spots, boundaries) — 5-8 rounds max (`skills/public/bootstrap/SKILL.md`)
- Surprise-me dynamically discovers available skills from `<available_skills>` at runtime and combines 1-3 of them into a single cohesive deliverable — it does not hardcode which skills to use (`skills/public/surprise-me/SKILL.md`)

## Decisions
- Skill-creator description optimization uses a 60/40 train/test split with 3 runs per query to get reliable trigger rates — the best description is selected by test score, not train score, to avoid overfitting (`skills/public/skill-creator/SKILL.md`)
- Bootstrap extraction tracker has 7 required fields and 3 nice-to-have fields — if still missing required fields after 8 rounds, the skill makes its best inference and confirms with the user (`skills/public/bootstrap/SKILL.md`)
- Vercel deploy requires no authentication — it returns a Preview URL (live site) and a Claim URL (to transfer the deployment to the user's Vercel account) (`skills/public/vercel-deploy-claimable/SKILL.md`)

## Patterns
- Skill-creator organizes evaluation results by iteration: `<workspace>/iteration-N/eval-<ID>/` with `with_skill/` and `without_skill/` (or `old_skill/`) subdirectories — timing data is captured from subagent task notifications and saved to `timing.json` immediately (`skills/public/skill-creator/SKILL.md`)
- Code-documentation adapts output scope to project size: single file → inline comments, small library → README + API reference, medium project → README + API docs + examples, large project → full documentation suite (`skills/public/code-documentation/SKILL.md`)
- DeerFlow context modes map to capability levels: Flash (no thinking/planning/subagents) → Standard (thinking only) → Pro (thinking + planning) → Ultra (thinking + planning + subagents) (`skills/public/claude-to-deerflow/SKILL.md`)
- Skill-creator test cases use realistic user prompts with concrete details (file paths, column names, company names, typos, casual speech) — abstract requests like "Format this data" are rejected as poor test cases (`skills/public/skill-creator/SKILL.md`)

## Dependencies
- Skill-creator's eval pipeline depends on subagents (the `task` tool) for parallel test execution — without subagents, baseline comparisons and quantitative benchmarking are skipped (`skills/public/skill-creator/SKILL.md`)
- Skill-creator's description optimization depends on `claude -p` CLI — this is Claude Code only; on Claude.ai this section is skipped (`skills/public/skill-creator/SKILL.md`)
- Bootstrap depends on the `setup_agent` tool being available — this tool persists SOUL.md and finalizes agent setup (`skills/public/bootstrap/SKILL.md`)
- Find-skills depends on `npx skills` CLI being installed — it searches the open agent skills ecosystem at https://skills.sh/ (`skills/public/find-skills/SKILL.md`)

## Skill Lifecycle
- New skills are created via `init_skill.py` which scaffolds the directory structure (SKILL.md, scripts/, references/, templates/, assets/) (`skills/public/skill-creator/scripts/init_skill.py`)
- Skills are packaged via `package_skill.py` into a `.skill` file for distribution — the resulting file can be installed by other users (`skills/public/skill-creator/scripts/package_skill.py`)
- Skill frontmatter is validated via `quick_validate.py` — this runs in CI against every bundled SKILL.md under `skills/public/` (`skills/public/skill-creator/scripts/quick_validate.py`, `git:b90f219b`)
- Skill descriptions are optimized via `run_loop.py` which iteratively improves the frontmatter description for better triggering accuracy using an eval set of should-trigger/should-not-trigger queries (`skills/public/skill-creator/scripts/run_loop.py`)

## DeerFlow Integration
- DeerFlow SSE stream events include: `metadata` (run_id), `values` (full state with messages), `messages-tuple` (incremental AI text/tool updates), `end` (stream complete) (`skills/public/claude-to-deerflow/SKILL.md`)
- DeerFlow file uploads support PDF, PPTX, XLSX, DOCX — all are automatically converted to Markdown on upload (`skills/public/claude-to-deerflow/SKILL.md`)
- DeerFlow thread IDs persist across sessions — conversations can be continued later by reusing the same thread_id (`skills/public/claude-to-deerflow/SKILL.md`)
