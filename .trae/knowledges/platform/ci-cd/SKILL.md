---
name: knowledge-platform-ci-cd
description: >
  Covers GitHub Actions CI/CD pipelines: linting, unit tests, E2E tests, replay contract
  verification, blocking IO gates, PR/issue labeling automation, label synchronization,
  and container publishing.
  Navigate when: adding or modifying CI workflows, debugging pipeline failures, understanding
  PR labeling rules, setting up new automated checks, or troubleshooting CI-specific issues.
  Excludes: Docker infrastructure (see ../docker-infrastructure/), operational scripts (see ../operational-scripts/).
  Keywords: GitHub Actions, CI, CD, lint, unit tests, E2E, Playwright, replay, triage,
  labeler, pull_request_target, concurrency, Blockbuster, ruff, eslint, prettier.
---

## Module Structure

CI/CD pipelines automate code quality enforcement, testing, labeling, and container publishing
for DeerFlow. All workflows live under `.github/workflows/` and use GitHub Actions with
`ubuntu-latest` runners. The labeling workflows use `pull_request_target` for safety — they
read metadata via the API without checking out or executing PR code.

### Directory Layout
- `.github/workflows/lint-check.yml` — Backend (ruff) + frontend (eslint, prettier, typecheck, build)
- `.github/workflows/backend-unit-tests.yml` — Backend pytest suite (Python 3.12, uv)
- `.github/workflows/frontend-unit-tests.yml` — Frontend test suite
- `.github/workflows/e2e-tests.yml` — Playwright E2E tests (Chromium, mocked APIs)
- `.github/workflows/backend-blocking-io-tests.yml` — Blockbuster async blocking IO runtime gate
- `.github/workflows/replay-e2e.yml` — Record/replay front-back contract verification (2 layers)
- `.github/workflows/triage.yml` — Consolidated PR/issue labeling (area, size, risk, needs-validation, reviewing, needs-triage)
- `.github/workflows/label-sync.yml` — Declarative label sync from `.github/labels.yml`
- `.github/labels.yml` — Declarative source of truth for 29 namespaced labels
- `.github/labeler.yml` — Legacy path-based label rules (superseded by triage.yml in-script rules)

### Key Entry Points
- `lint-check.yml` — Runs on push to main and all PRs; blocks merge on failure
- `backend-unit-tests.yml` — Runs on push to main and PRs; 15-minute timeout
- `triage.yml` — Runs on `pull_request_target` (opened, synchronize, reopened, ready_for_review), `pull_request_review` (submitted), and `issues` (opened)
- `replay-e2e.yml` — Runs on push to main and PRs, triggered by changes on either side of the front-back contract
- `label-sync.yml` — Runs when `.github/labels.yml` changes on main, or manually via workflow_dispatch

## Gotchas
- `triage.yml` uses `pull_request_target` but NEVER checks out or runs PR code — it reads changed-file lists and PR fields via the GitHub API only; this is critical for fork PR safety (`.github/workflows/triage.yml`)
- The `reviewing` job in triage.yml gates on `author_association in {OWNER, MEMBER, COLLABORATOR}` AND `user.type === 'User'` — the previous implementation called `getCollaboratorPermissionLevel` which 404'd on bot reviewers like Copilot and crashed the job (`.github/workflows/triage.yml`, `git:90e23bfd`)
- `triage.yml` reads labels LIVE via `listLabelsOnIssue` (paginated, per_page:100) rather than from the stale event payload, so rapid synchronize events converge instead of thrashing (`.github/workflows/triage.yml`, `git:90e23bfd`)
- The `replay-e2e.yml` workflow is triggered by changes on EITHER side of the front-back contract — if you add a new backend endpoint that the frontend consumes, you must add its path to the trigger list (`.github/workflows/replay-e2e.yml`)
- `lint-check.yml` builds the frontend as part of linting (`BETTER_AUTH_SECRET=local-dev-secret pnpm build`) — a type error that only surfaces at build time will fail this check (`.github/workflows/lint-check.yml`)
- `backend-unit-tests.yml` uses `concurrency` with `cancel-in-progress: true` grouped by PR number — pushing new commits cancels the previous run, which can mask flaky tests (`.github/workflows/backend-unit-tests.yml`)
- The `label-sync.yml` workflow is additive/update-only and never deletes labels — labels removed from `.github/labels.yml` must be manually deleted from the repository (`.github/workflows/label-sync.yml`, `git:aca7acc1`)
- `e2e-tests.yml` uses a `paths` filter on push/PR triggers — changes outside the frontend directory will NOT trigger E2E tests, even if they affect the front-back contract (`.github/workflows/e2e-tests.yml`)

## Architecture
- All CI workflows follow a consistent pattern: checkout → setup language runtime → install deps → run checks, with `timeout-minutes` set on each job (`.github/workflows/`)
- The triage system was consolidated from three separate workflows (pr-labeler, pr-triage, issue-triage) into a single `triage.yml` to eliminate label thrashing from concurrent jobs (`.github/workflows/triage.yml`, `git:90e23bfd`)
- Replay E2E uses a two-layer approach: Layer 1 replays recorded LLM traces through the real gateway and asserts SSE event sequences match committed golden files; Layer 2 runs the real Next.js frontend + replay gateway + Chromium and asserts DOM rendering (`.github/workflows/replay-e2e.yml`)
- The blocking IO gate uses Blockbuster (`blockbuster>=1.5.26`) scoped to `app.*` and `deerflow.*` to catch sync blocking calls on the asyncio event loop, with `@pytest.mark.allow_blocking_io` opt-out (`.github/workflows/backend-blocking-io-tests.yml`)
- PR labeling computes area labels from path rules defined inline in the workflow script (not from `.github/labeler.yml`), size from churn (excluding lockfiles/snapshots), and risk from changed paths (`.github/workflows/triage.yml`)

## Decisions
- Consolidated PR/issue labeling into a single `triage.yml` to fix the `reviewing` job crash (404 on bot reviewers) and eliminate label thrash from concurrent labeler jobs (`.github/workflows/triage.yml`, `git:90e23bfd`)
- Replaced `actions/labeler` with inline path rules in the triage script to avoid the sync-labels action removing labels outside its config (`.github/workflows/triage.yml`, `git:90e23bfd`)
- Each triage job only reconciles labels in namespaces it owns (area:*, size/*, risk:*, needs-validation) — it never touches labels applied by maintainers or other tools (`.github/workflows/triage.yml`)
- The `first-time-contributor` and `reviewing` labels are add-only to prevent automation from removing them after they're applied (`.github/workflows/triage.yml`)

## Patterns
- All workflows use `concurrency` groups to cancel redundant runs: `group: <workflow>-${{ github.event.pull_request.number || github.ref }}` with `cancel-in-progress: true` (`.github/workflows/`)
- Backend workflows use `astral-sh/setup-uv@v7` for uv installation and `uv sync --group dev` for dependency installation (`.github/workflows/backend-unit-tests.yml`, `.github/workflows/lint-check.yml`)
- Frontend workflows use `corepack enable` + `corepack prepare pnpm@10.26.2 --activate` to pin the pnpm version, then `pnpm install --frozen-lockfile` (`.github/workflows/lint-check.yml`)
- Draft PRs are skipped via `if: github.event.pull_request.draft == false` in most workflows (`.github/workflows/backend-unit-tests.yml`, `.github/workflows/replay-e2e.yml`)

## Conventions
- Workflow files use `branches: ['main']` for push triggers and `branches: ['*']` or no branch filter for PR triggers (`.github/workflows/`)
- All workflows set minimal `permissions: contents: read` with additional permissions (pull-requests: write, issues: write) only where needed (`.github/workflows/`)
- Python version is pinned to `3.12` across all backend workflows (`.github/workflows/`)
- Node.js version is pinned to `22` across all frontend workflows (`.github/workflows/`)

## Dependencies
- `actions/checkout@v6` for repository checkout (`.github/workflows/`)
- `actions/setup-python@v6` with `python-version: '3.12'` for Python setup (`.github/workflows/`)
- `astral-sh/setup-uv@v7` for uv installation (`.github/workflows/`)
- `actions/setup-node@v4` with `node-version: '22'` for Node.js setup (`.github/workflows/`)
- `actions/github-script@v8` for inline JavaScript in triage/label workflows (`.github/workflows/triage.yml`, `.github/workflows/label-sync.yml`)
- `actions/upload-artifact@v4` for test report uploads in replay-e2e (`.github/workflows/replay-e2e.yml`)
- `blockbuster>=1.5.26,<1.6` in the backend dev group for blocking IO detection (`.github/workflows/backend-blocking-io-tests.yml`)

## CI Pipeline Flow
- On every PR: lint-check (backend ruff + frontend eslint/prettier/typecheck/build) + backend-unit-tests + frontend-unit-tests run in parallel; triage.yml applies labels (`.github/workflows/`)
- On push to main: all checks run; replay-e2e runs if contract-surface files changed; label-sync runs if `.github/labels.yml` changed (`.github/workflows/`)
- E2E tests and blocking-io tests are triggered by path filters and run as additional gates beyond the core lint+unit-test suite (`.github/workflows/e2e-tests.yml`, `.github/workflows/backend-blocking-io-tests.yml`)
- Container publishing (`container.yaml`) pushes Docker images on push to main (`.github/workflows/container.yaml`, `git:b10eb7ba`)
