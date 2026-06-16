## 085c13ed 2026-04-20 Reuben Bowlby
fix: remove unnecessary f-string prefixes and unused import (#2352)

- Remove f-string prefix on 7 strings with no placeholders (F541)
  in analyze.py, aggregate_benchmark.py, run_loop.py, generate_review.py
- Remove unused `os` import in quick_validate.py (F401)

Found by ruff via HUMMBL Arbiter (https://hummbl.io/audit).

- `skills/public/data-analysis/scripts/analyze.py`
- `skills/public/skill-creator/eval-viewer/generate_review.py`
- `skills/public/skill-creator/scripts/aggregate_benchmark.py`
- `skills/public/skill-creator/scripts/quick_validate.py`
- `skills/public/skill-creator/scripts/run_loop.py`

## b90f219b 2026-04-23 d 🔹
fix(skills): validate bundled SKILL.md front-matter in CI (fixes #2443) (#2457)

* fix(skills): validate bundled SKILL.md front-matter in CI (fixes #2443)

Adds a parametrized backend test that runs `_validate_skill_frontmatter`
against every bundled SKILL.md under `skills/public/`, so a broken
front-matter fails CI with a per-skill error message instead of
surfacing as a runtime gateway-load warning.

The new test caught two pre-existing breakages on `main` and fixes them:

* `bootstrap/SKILL.md`: the unquoted description had a second `:` mid-line
  ("Also trigger for updates: ..."), which YAML parses as a nested mapping
  ("mapping values are not allowed here"). Rewrites the description as a
  folded scalar (`>-`), which preserves the original wording (including the
  embedded colon, double quotes, and apostrophes) without further escaping.
  This complements PR #2436 (single-file colon→hyphen patch) with a more
  general convention that survives future edits.

* `chart-visualization/SKILL.md`: used `dependency:` which is not in
  `ALLOWED_FRONTMATTER_PROPERTIES`. Renamed to `compatibility:`, the
  documented field for "Required tools, dependencies" per skill-creator.
  No code reads `dependency` (verified by grep across backend/).

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* Fix the lint error

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `skills/public/bootstrap/SKILL.md`
  L3: description: >-
  L4: Generate a personalized SOUL.md through a warm, adaptive onboarding conversation.
  L5: Trigger when the user wants to create, set up, or initialize their AI partner's
  L6: identity — e.g., "create my SOUL.md", "bootstrap my agent", "set up my AI
  L7: partner", "define who you are", "let's do onboarding", "personalize this AI",
  L8: "make you mine", or when a SOUL.md is missing. Also trigger for updates:
  L9: "update my SOUL.md", "change my AI's personality", "tweak the soul".
- `skills/public/chart-visualization/SKILL.md`
  L4: compatibility:

## 84f88b66 2026-05-12 Eilen Shin
docs: align runtime docs with gateway mode (#2868)

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `skills/public/claude-to-deerflow/SKILL.md`
  L17: | Gateway API    | 8001        | `$DEERFLOW_GATEWAY_URL`          | REST endpoints and embedded agent runtime |
  L18: | LangGraph-compatible API | 8001 | `$DEERFLOW_LANGGRAPH_URL`       | Agent threads, runs, streaming   |

## cd5bedaa 2026-06-08 DanielWalnut
feat: MiniMax provider for image/video/podcast skills + new music-generation skill (#3437)

* docs(spec): MiniMax integration for generation skills + new music skill

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* docs(plan): MiniMax generation providers implementation plan

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* test(skills): add importlib loader + FakeResp for skill tests

* test(skills): register loaded module in sys.modules; raise requests.HTTPError in FakeResp

* feat(image-generation): add MiniMax provider with env auto-detect

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* refactor(image-generation): guard unknown provider, derive ref MIME, strengthen tests

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* feat(video-generation): add MiniMax provider with async poll/download

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* refactor(video-generation): surface base_resp errors while polling; add timeout test

* feat(podcast-generation): add MiniMax t2a_v2 provider with env auto-detect

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* refactor(podcast-generation): restore TTS credential guard; add volcengine + voice tests

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(music-generation): new MiniMax music skill via skill-creator

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* refactor(music-generation): treat empty lyrics as absent; test no-audio-data path

* refactor(skills): add request timeouts to MiniMax network calls

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* Potential fix for pull request finding 'Explicit returns mixed with implicit (fall through) returns'

Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

* fix(models): strip inconsistent user-message names for MiniMax chat

DeerFlow middlewares tag user messages with provenance names (user-input, summary, loop_warning); langchain serializes them into the OpenAI-compatible payload and MiniMax rejects mismatched user-message names with "user name must be consistent (2013)". PatchedChatMiniMax now drops the per-message name from user-role messages. Point the config.example MiniMax models at PatchedChatMiniMax so they also get reasoning_content mapping.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* feat(image-generation): MiniMax sends JSON prompt field, guard 1500-char limit

MiniMax image-01 takes one text string capped at 1500 chars, but the skill was sending the whole structured JSON. The MiniMax provider now extracts the JSON `prompt` field (relying on prompt_optimizer to expand it) and fails fast with a clear error before calling the API when that field exceeds 1500 chars. Authoring stays provider-agnostic; Gemini still receives the full JSON.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* feat(podcast-generation): per-provider TTS concurrency and retry/backoff

Each TTS provider owns its concurrency internally — MiniMax runs single-threaded to reduce rate-limit failures, Volcengine keeps 4 workers — with automatic retry and backoff on transient HTTP and base_resp errors. No caller-facing concurrency knob.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(skills): address Copilot review comments on generation skills

- video: add raise_for_status + timeout to the Gemini download/POST/poll calls so non-2xx responses surface as clear HTTP errors instead of JSON/KeyError or hangs
- video: check the task Fail status before the generic base_resp check so the failure keeps its task_id context
- video/image: create the output file parent directory before writing (matching music-generation) so nested output paths do not raise FileNotFoundError
- music: require a non-empty prompt and fail fast with ValueError instead of sending an empty prompt to the API

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(scripts): reclaim dev ports across worktrees in make stop/dev

All deer-flow worktrees (main checkout + linked worktrees) hardcode the same dev ports (8001/3000/2026), so a service started from any worktree must be reclaimable from another. stop_all now resolves the set of worktree roots (DEERFLOW_ROOTS) and treats a process as deer-flow-owned when its open files live under any of them. It also force-kills survivors on 2026 alongside 8001/3000, fixing `make dev` aborting on the nginx port preflight when a prior nginx lingered on 2026.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(view-image): hide the injected image-context message from the UI

ViewImageMiddleware injects a HumanMessage (text + base64 images) so the vision model can see viewed images, but it was the only internal injector that set neither hide_from_ui nor a hidden name, so it leaked into the chat UI (and IM channels) as a user bubble reading "Here are the images you've viewed:". Mark it with additional_kwargs={"hide_from_ui": True}, matching todo/dynamic_context injections, which the frontend isHiddenFromUIMessage and the channel sender already honor. The model still receives the full content.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(minimax): mark M2.7 models as text-only (no vision)

MiniMax M2.7 / M2.7-highspeed do not support vision; only M3 does. The
provider config asserted vision support for M2.7 in four places.

- config.example.yaml: 4 M2.7 entries -> supports_vision: false
- backend/docs/CONFIGURATION.md: M2.7 + highspeed -> supports_vision: false
- wizard: add LLMProvider.model_vision_overrides + extra_config_for() so
  selecting an M2.7 model writes supports_vision: false while M3 (default)
  keeps vision; wire it through setup_wizard.py
- tests: M2.7-highspeed fixture -> supports_vision=False; add
  test_minimax_vision_is_per_model

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

- `skills/public/image-generation/SKILL.md`
  L181: ## Providers (Gemini / MiniMax)
  L182: 
  L183: This skill auto-selects the provider by environment variables (no CLI change):
  L184: 
  L185: - `GEMINI_API_KEY` set → use Gemini (default, unchanged).
  L186: - Only `MINIMAX_API_KEY` set → use MiniMax (`/v1/image_generation`, model `image-01`).
  L187: - Force one explicitly with `IMAGE_GENERATION_PROVIDER=gemini|minimax`.
  L188: 
  L189: MiniMax optional overrides: `MINIMAX_API_HOST` (default `https://api.minimaxi.com`),
  L190: `MINIMAX_IMAGE_MODEL` (default `image-01`). Reference images are sent as the MiniMax
  L191: `subject_reference` character image. The CLI and `--prompt-file` / `--reference-images`
  L192: / `--output-file` / `--aspect-ratio` arguments are identical for both providers.
  L193: 
  L194: **MiniMax prompt handling (provider-internal).** Authoring is provider-agnostic — write
  L195: the same structured JSON regardless of which provider is active. MiniMax `image-01`
  L196: consumes a single text string, so the MiniMax path itself sends only the JSON `prompt`
  L197: field (the other fields such as `style` / `composition` / `negative_prompt` apply to the
  L198: Gemini path) and enables `prompt_optimizer` so MiniMax expands it server-side. MiniMax
  L199: caps that prompt at 1500 characters; if the `prompt` field is longer, the script returns
  L200: an error instead of calling the API. The Gemini path receives the full structured JSON.
  ... (truncated)
- `skills/public/image-generation/scripts/generate.py`
  L8: # MiniMax image-01 caps the prompt at 1500 characters and rejects longer requests
  L9: # with a generic "invalid params" error, so validate before calling the API.
  L14: """Validate if an image file can be opened and is not corrupted."""
  L29: """Pick the generation provider.
  L34: """
  L78: """Create the output file's parent directory so nested paths don't fail."""
  L85: """Extract the single text prompt MiniMax image-01 expects.
  L93: """
  L128: # Reference images are passed as character subjects as-is; unlike the Gemini
  L129: # path we do not pre-validate them — invalid files surface as a MiniMax API error.
- `skills/public/music-generation/SKILL.md`
  L1: ---
  L2: name: music-generation
  L3: description: Use this skill when the user requests to generate, create, compose, or produce music or songs — background music, theme songs, jingles, or instrumental tracks. Generates a song from a style/mood prompt and optional lyrics via the MiniMax music API.
  L4: ---
  L5: 
  L6: # Music Generation Skill
  L7: 
  L8: ## Overview
  L9: 
  L10: This skill generates songs (vocal or instrumental) from a structured JSON spec using the
  L11: MiniMax music generation API (`/v1/music_generation`). You describe the style/mood/scene in
  L12: `prompt`, optionally provide `lyrics`, and the script returns an MP3.
  L13: 
  L14: ## Workflow
  L15: 
  L16: ### Step 1: Understand Requirements
  L17: 
  L18: Identify the desired style, mood, scene, language, and whether the user wants vocals or a
  L19: pure instrumental track. Decide whether to supply lyrics or let the model write them.
  L20: 
  ... (truncated)
- `skills/public/music-generation/scripts/generate.py`
  L17: """Generate a song from a JSON spec via MiniMax /v1/music_generation.
  L23: """
- `skills/public/podcast-generation/SKILL.md`
  L67: > - The TTS provider and its concurrency are selected automatically from environment variables — you do not choose or tune them.
  L176: - For Volcengine: `VOLCENGINE_TTS_APPID` and `VOLCENGINE_TTS_ACCESS_TOKEN`
  L177: - For MiniMax: `MINIMAX_API_KEY`
  L187: 
  L188: ## Providers (Volcengine / MiniMax)
  L189: 
  L190: Auto-selected by environment variables:
  L191: 
  L192: - `VOLCENGINE_TTS_APPID` + `VOLCENGINE_TTS_ACCESS_TOKEN` set → Volcengine TTS (default).
  L193: - Only `MINIMAX_API_KEY` set → MiniMax TTS (`/v1/t2a_v2`).
  L194: - Force with `PODCAST_GENERATION_PROVIDER=volcengine|minimax`.
  L195: 
  L196: MiniMax overrides: `MINIMAX_API_HOST` (default `https://api.minimaxi.com`),
  L197: `MINIMAX_TTS_MODEL` (default `speech-2.6-hd`), `MINIMAX_TTS_VOICE_MALE`
  L198: (default `male-qn-qingse`), `MINIMAX_TTS_VOICE_FEMALE` (default `female-tianmei`).
  L199: 
  L200: Concurrency is owned by each provider internally — MiniMax runs single-threaded
  L201: to reduce rate-limit failures, Volcengine uses 4 workers. There is no
  L202: caller-facing concurrency knob; transient rate limits are handled by automatic
  L203: retry with backoff.
- `skills/public/podcast-generation/scripts/generate.py`
  L18: # MiniMax base_resp codes worth retrying: unknown, timeout, RPM limit, TPM limit.
  L82: """Each provider owns its own concurrency: MiniMax stays low to avoid rate
  L84: """
  L91: """Return the server-provided Retry-After (seconds), if any."""
  L101: """Sleep with exponential backoff + jitter, honoring Retry-After when present.
  L105: """
  L113: """Convert text to speech using Volcengine TTS (returns base64-decoded mp3 bytes).
  L116: """
  L166: """Convert text to speech using MiniMax t2a_v2 (returns hex-decoded mp3 bytes).
  L171: """
  L253: """Convert script lines to audio chunks using TTS with multi-threading.
  L259: """
- `skills/public/video-generation/SKILL.md`
  L140: 
  L141: ## Providers (Gemini / MiniMax)
  L142: 
  L143: Auto-selected by environment variables (CLI unchanged):
  L144: 
  L145: - `GEMINI_API_KEY` set → Gemini Veo (default, unchanged).
  L146: - Only `MINIMAX_API_KEY` set → MiniMax video (`/v1/video_generation`, async 3-step poll/download).
  L147: - Force with `VIDEO_GENERATION_PROVIDER=gemini|minimax`.
  L148: 
  L149: MiniMax overrides: `MINIMAX_API_HOST` (default `https://api.minimaxi.com`),
  L150: `MINIMAX_VIDEO_MODEL` (default `MiniMax-Hailuo-2.3`). The first reference image is used
  L151: as MiniMax `first_frame_image`. MiniMax ignores `--aspect-ratio` (it uses resolution/duration).
- `skills/public/video-generation/scripts/generate.py`
  L11: """Pick the provider: <SKILL>_PROVIDER override > existing creds > MiniMax fallback."""
  L30: """Create the output file's parent directory so nested paths don't fail."""
  L79: # Surface query-level errors (bad task_id, auth) that arrive as a non-zero
  L80: # base_resp without a terminal status, then keep polling.
  L199: # MiniMax video uses resolution/duration, not aspect_ratio; aspect_ratio ignored.

