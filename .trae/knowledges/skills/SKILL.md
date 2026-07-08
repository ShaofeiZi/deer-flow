---
name: knowledge-skills
description: >
  Covers the skills ecosystem: all bundled agent skills under skills/public/, their
  shared patterns, provider architecture, and inter-skill dependencies.
  Navigate when: adding a new skill, modifying skill frontmatter, debugging skill
  triggering, understanding provider auto-detection, or analyzing cross-skill coupling.
  Excludes: individual skill implementations (see subdomain nodes).
  Keywords: skill, SKILL.md, frontmatter, provider, MiniMax, Gemini, Volcengine,
  _resolve_provider, skill-creator, image-generation, podcast-generation,
  video-generation, music-generation, deep-research, data-analysis.
---

## Module Structure

All agent skills live under `skills/public/`. Each skill is a self-contained directory
with a SKILL.md entry point and optional bundled resources (scripts/, references/,
templates/, assets/). Skills are loaded via a three-level progressive disclosure system:
metadata (name + description) → SKILL.md body → bundled resources on demand.

### Directory Layout
- `skills/public/` — All bundled skills
  - `image-generation/` — AI image generation (Gemini / MiniMax)
  - `music-generation/` — AI music generation (MiniMax only)
  - `video-generation/` — AI video generation (Gemini / MiniMax)
  - `podcast-generation/` — Text-to-podcast audio (Volcengine / MiniMax)
  - `ppt-generation/` — Presentation generation from slide images
  - `newsletter-generation/` — Curated newsletter creation
  - `frontend-design/` — Production-grade web UI generation
  - `web-design-guidelines/` — UI compliance review against web guidelines
  - `chart-visualization/` — 26 chart types via AntV Studio API
  - `data-analysis/` — Excel/CSV analysis via DuckDB SQL engine
  - `consulting-analysis/` — McKinsey/BCG-style research reports
  - `deep-research/` — Multi-angle web research methodology
  - `github-deep-research/` — GitHub repo deep-dive analysis
  - `academic-paper-review/` — Single-paper peer review
  - `systematic-literature-review/` — Multi-paper arXiv survey
  - `skill-creator/` — Meta-skill for creating and evaluating skills
  - `code-documentation/` — API/README/architecture doc generation
  - `bootstrap/` — Conversational SOUL.md onboarding
  - `claude-to-deerflow/` — DeerFlow HTTP API client
  - `find-skills/` — Skill discovery via npx skills CLI
  - `vercel-deploy-claimable/` — Vercel deployment without auth
  - `surprise-me/` — Creative skill mashup generator

### Key Entry Points
- Each skill's `SKILL.md` — Primary trigger and instruction document
- `skill-creator/SKILL.md` — Meta-skill for creating new skills
- `skill-creator/scripts/init_skill.py` — New skill scaffolding

## Gotchas
- SKILL.md frontmatter must use `compatibility:` not `dependency:` — `dependency:` is not in ALLOWED_FRONTMATTER_PROPERTIES and will fail CI validation (`skills/public/chart-visualization/SKILL.md`, `git:b90f219b`)
- Multi-line descriptions containing colons must use YAML folded scalar (`>-`) — unquoted colons parse as nested mappings and break the gateway (`skills/public/bootstrap/SKILL.md`, `git:b90f219b`)
- The `_resolve_provider()` function signature is identical across image/video/podcast generation scripts but each has its own copy — changes to the provider resolution logic must be replicated in all three (`skills/public/image-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`, `skills/public/podcast-generation/scripts/generate.py`)
- Frontmatter validation runs in CI against every bundled SKILL.md — a broken frontmatter fails CI with per-skill error messages, not just a runtime gateway-load warning (`git:b90f219b`)

## Architecture
- All generation skills follow a consistent provider pattern: `_resolve_provider(override_env, existing_provider, has_existing_creds)` → provider-specific generation function, with MiniMax as the universal fallback when `MINIMAX_API_KEY` is set (`skills/public/image-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`, `skills/public/podcast-generation/scripts/generate.py`)
- Skills use progressive disclosure: the frontmatter `description` field is the sole trigger mechanism — the agent decides whether to load a skill based solely on name + description before seeing the body (`skills/public/skill-creator/SKILL.md`)
- PPT generation is a composite skill that depends on image-generation — it generates slide images via image-generation's script, then composes them into PPTX (`skills/public/ppt-generation/SKILL.md`)
- The skill-creator is the only meta-skill — it has its own eval/benchmark pipeline with grader, comparator, and analyzer sub-agents (`skills/public/skill-creator/agents/`)

## Decisions
- MiniMax was added as a secondary provider across image/video/podcast/music skills in a single large commit rather than incremental per-skill additions — this means all four skills share the same provider resolution pattern (`git:cd5bedaa`)
- Podcast TTS concurrency is provider-owned internally (MiniMax=1 worker, Volcengine=4 workers) with no caller-facing knob — this design prevents users from accidentally exceeding rate limits (`skills/public/podcast-generation/scripts/generate.py`, `git:cd5bedaa`)

## Patterns
- All generation skills accept `--prompt-file` (JSON spec) and `--output-file` (output path) as CLI arguments — the caller never reads the Python script, only invokes it (`skills/public/image-generation/SKILL.md`, `skills/public/music-generation/SKILL.md`, `skills/public/video-generation/SKILL.md`)
- Skills that call external APIs use `_check_base_resp()` to validate MiniMax responses — the pattern checks `base_resp.status_code != 0` and raises with the error message (`skills/public/image-generation/scripts/generate.py`, `skills/public/music-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`)
- Research skills form a dependency chain: deep-research is the foundational methodology, github-deep-research and systematic-literature-review build on it, consulting-analysis consumes research output in Phase 2 (`skills/public/deep-research/SKILL.md`, `skills/public/consulting-analysis/SKILL.md`)

## Dependencies
- MiniMax API key (`MINIMAX_API_KEY`) is the universal fallback credential for image, video, podcast, and music generation — if set, it auto-activates the MiniMax provider path (`skills/public/image-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`, `skills/public/podcast-generation/scripts/generate.py`, `skills/public/music-generation/scripts/generate.py`)
- Chart-visualization depends on the AntV Studio API at `https://antv-studio.alipay.com/api/gpt-vis` — all 26 chart types are rendered server-side (`skills/public/chart-visualization/scripts/generate.js`)
- Data-analysis depends on DuckDB and openpyxl — both are auto-installed via pip if missing at import time (`skills/public/data-analysis/scripts/analyze.py`)

## Child Knowledge Nodes
- `./content-creation/SKILL.md` — Navigate when: working with image/video/music/podcast/PPT/newsletter generation, frontend design, chart visualization, or web design guidelines
- `./data-analysis/SKILL.md` — Navigate when: analyzing Excel/CSV data, generating consulting reports, or building analysis frameworks
- `./research/SKILL.md` — Navigate when: conducting web research, GitHub repo analysis, academic paper review, or systematic literature surveys
- `./development/SKILL.md` — Navigate when: creating/modifying skills, generating code documentation, bootstrapping agent identity, deploying to Vercel, or discovering skills
