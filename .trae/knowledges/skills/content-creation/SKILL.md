---
name: knowledge-skills-content-creation
description: >
  Covers content creation skills: image, video, music, and podcast generation,
  PPT creation, newsletter writing, frontend design, web design guidelines review,
  and chart visualization.
  Navigate when: generating any media content, creating presentations, designing
  web UIs, reviewing UI compliance, or visualizing data as charts.
  Excludes: data analysis (see ../data-analysis/), research (see ../research/),
  development tooling (see ../development/).
  Keywords: image-generation, video-generation, music-generation, podcast-generation,
  ppt-generation, newsletter-generation, frontend-design, web-design-guidelines,
  chart-visualization, MiniMax, Gemini, Volcengine, TTS, slide, prompt, aspect-ratio.
---

## Module Structure

Content creation skills generate media assets (images, videos, music, podcasts),
documents (presentations, newsletters), web UIs, and data visualizations. Most
generation skills follow a common pattern: JSON spec → Python/Node script → output file.
Multi-provider skills auto-detect the active provider from environment variables.

### Directory Layout
- `skills/public/image-generation/` — AI image generation (Gemini Imagen / MiniMax image-01)
  - `scripts/generate.py` — Provider dispatch + generation logic
  - `templates/doraemon.md` — Doraemon comic style template
- `skills/public/video-generation/` — AI video generation (Gemini Veo / MiniMax Hailuo)
  - `scripts/generate.py` — Async poll/download for MiniMax, direct for Gemini
- `skills/public/music-generation/` — AI music generation (MiniMax only)
  - `scripts/generate.py` — Song generation from style/lyrics spec
- `skills/public/podcast-generation/` — Text-to-podcast audio
  - `scripts/generate.py` — TTS synthesis with multi-threading and retry/backoff
  - `templates/tech-explainer.md` — Technical content podcast template
- `skills/public/ppt-generation/` — Presentation generation
  - `scripts/generate.py` — PPTX composition from slide images
- `skills/public/newsletter-generation/` — Curated newsletter creation
- `skills/public/frontend-design/` — Production-grade web UI generation
- `skills/public/web-design-guidelines/` — UI compliance review
- `skills/public/chart-visualization/` — 26 chart types via AntV Studio
  - `scripts/generate.js` — Chart generation via HTTP API
  - `references/` — Per-chart-type parameter specifications

### Key Entry Points
- `generate_image()` in `skills/public/image-generation/scripts/generate.py` — Image generation entry
- `generate_music()` in `skills/public/music-generation/scripts/generate.py` — Music generation entry
- `generate_podcast()` in `skills/public/podcast-generation/scripts/generate.py` — Podcast TTS entry
- `main()` in `skills/public/chart-visualization/scripts/generate.js` — Chart generation entry

## Gotchas
- MiniMax image-01 caps prompts at 1500 characters — longer prompts fail with a generic "invalid params" error; the script validates length before calling the API (`skills/public/image-generation/scripts/generate.py`)
- PPT slides MUST be generated sequentially, never in parallel — each slide uses the previous slide as a reference image for visual consistency; parallel generation breaks the reference chain (`skills/public/ppt-generation/SKILL.md`)
- MiniMax video generation is async (submit → poll → download, 3-step) while Gemini is synchronous — the caller must not assume the same latency profile for both providers (`skills/public/video-generation/scripts/generate.py`)
- Podcast TTS MiniMax provider runs single-threaded (`DEFAULT_MINIMAX_MAX_WORKERS = 1`) to avoid rate-limit failures, while Volcengine uses 4 workers — this is not user-tunable (`skills/public/podcast-generation/scripts/generate.py`)
- Music generation is MiniMax-only with no multi-provider fallback — if `MINIMAX_API_KEY` is not set, generation fails immediately unlike image/video/podcast which have Gemini/Volcengine alternatives (`skills/public/music-generation/scripts/generate.py`)
- The `_resolve_provider()` function is copy-pasted across image/video/podcast scripts with identical logic but different env var names — fixing a bug in one requires fixing all three (`skills/public/image-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`, `skills/public/podcast-generation/scripts/generate.py`)
- Frontend-design output MUST name the entry HTML file `index.html` — this is a strict requirement for Vercel deployment compatibility (`skills/public/frontend-design/SKILL.md`)
- Chart-visualization uses `compatibility:` not `dependency:` in frontmatter — using `dependency:` fails CI because it's not in ALLOWED_FRONTMATTER_PROPERTIES (`skills/public/chart-visualization/SKILL.md`, `git:b90f219b`)

## Architecture
- All multi-provider generation skills follow the same provider resolution chain: explicit `<SKILL>_PROVIDER` env override → existing provider credentials → MiniMax fallback if `MINIMAX_API_KEY` is set → error if no credentials (`skills/public/image-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`, `skills/public/podcast-generation/scripts/generate.py`)
- PPT generation is a composite/orchestrator skill — it does not generate images itself but delegates to image-generation, then composes the resulting images into PPTX (`skills/public/ppt-generation/SKILL.md`)
- Chart-visualization delegates rendering to AntV Studio's server-side API — the local script only constructs the payload and sends it via HTTP POST (`skills/public/chart-visualization/scripts/generate.js`)
- Frontend-design has a mandatory "Created By Deerflow" branding requirement embedded in every generated UI — the signature must be a clickable link to https://deerflow.tech (`skills/public/frontend-design/SKILL.md`)
- Web-design-guidelines fetches its rules dynamically from a GitHub raw URL before each review — the rules are not bundled locally (`skills/public/web-design-guidelines/SKILL.md`)

## Decisions
- MiniMax image-01 uses `prompt_optimizer: true` server-side — the skill sends only the JSON `prompt` field (not the full structured JSON) and lets MiniMax expand it, while Gemini receives the complete structured JSON (`skills/public/image-generation/scripts/generate.py`, `git:cd5bedaa`)
- Podcast TTS retry/backoff is automatic and provider-internal — MiniMax retryable codes are {1000, 1001, 1002, 1039} (unknown, timeout, RPM limit, TPM limit) with exponential backoff + jitter, honoring server `Retry-After` headers (`skills/public/podcast-generation/scripts/generate.py`, `git:cd5bedaa`)
- Music generation uses `music-2.6-free` as the default model — this works for all API-key users; paid users can set `MINIMAX_MUSIC_MODEL=music-2.6` for higher limits (`skills/public/music-generation/SKILL.md`)

## Patterns
- All generation skills use the same CLI pattern: `--prompt-file` (JSON spec input) + `--output-file` (output path) — the caller never reads the Python script, only invokes it with arguments (`skills/public/image-generation/SKILL.md`, `skills/public/music-generation/SKILL.md`, `skills/public/video-generation/SKILL.md`, `skills/public/podcast-generation/SKILL.md`)
- MiniMax API responses are validated via `_check_base_resp()` which checks `base_resp.status_code == 0` — non-zero codes raise exceptions with the status message (`skills/public/image-generation/scripts/generate.py`, `skills/public/music-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`)
- Output file parent directories are created via `_ensure_output_dir()` before writing — this prevents `FileNotFoundError` for nested output paths (`skills/public/image-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`, `git:cd5bedaa`)
- Newsletter generation uses a 4-phase workflow: Planning → Research & Curation → Writing → Assembly & Polish, with deep-research as a recommended companion skill (`skills/public/newsletter-generation/SKILL.md`)

## Dependencies
- Image, video, and podcast generation all depend on the `requests` library for HTTP calls to provider APIs (`skills/public/image-generation/scripts/generate.py`, `skills/public/video-generation/scripts/generate.py`, `skills/public/podcast-generation/scripts/generate.py`)
- Image generation Gemini path depends on `Pillow` (PIL) for reference image validation — it's lazy-imported so the module stays importable without it (`skills/public/image-generation/scripts/generate.py`)
- Chart-visualization requires Node.js >= 18.0.0 and depends on the AntV Studio API being reachable (`skills/public/chart-visualization/SKILL.md`, `skills/public/chart-visualization/scripts/generate.js`)
- PPT generation depends on image-generation being available — it reads image-generation's SKILL.md and calls its generate.py script (`skills/public/ppt-generation/SKILL.md`)

## Provider-Specific Behavior
- MiniMax video ignores `--aspect-ratio` — it uses resolution/duration instead; the CLI argument is silently ignored on the MiniMax path (`skills/public/video-generation/SKILL.md`, `git:cd5bedaa`)
- MiniMax image reference images are sent as `subject_reference` character images without pre-validation — invalid files surface as MiniMax API errors, unlike Gemini which validates images before sending (`skills/public/image-generation/scripts/generate.py`)
- MiniMax podcast TTS uses `t2a_v2` endpoint with configurable voice models — male default is `male-qn-qingse`, female default is `female-tianmei` (`skills/public/podcast-generation/SKILL.md`)
- Gemini image generation uses `gemini-3-pro-image-preview` model with `imageConfig.aspectRatio` — this is hardcoded, not configurable via env vars (`skills/public/image-generation/scripts/generate.py`)
