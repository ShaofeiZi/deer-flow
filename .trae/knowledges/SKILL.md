---
name: knowledge-deerflow
description: >
  DeerFlow is an open-source super agent harness that orchestrates sub-agents,
  memory, and sandboxes through extensible skills. Full-stack architecture with
  a Python/FastAPI backend, Next.js 16 frontend, and Docker-based deployment.
  Navigate when: understanding project architecture, onboarding, debugging
  cross-domain issues, adding new features, modifying agent behavior.
  Keywords: deerflow, agent, langgraph, sandbox, skill, mcp, fastapi, nextjs,
  super-agent, harness, orchestration, memory, tool, middleware.
---

## Module Structure

```
deer-flow/
├── backend/
│   ├── packages/harness/deerflow/    # Core agent framework (deerflow-harness package)
│   │   ├── agents/                   # Agent orchestration (lead agent, middlewares, subagents)
│   │   ├── sandbox/                  # Sandbox execution abstraction
│   │   ├── tools/                    # Tool ecosystem (builtins, community)
│   │   ├── mcp/                      # MCP integration
│   │   ├── models/                   # LLM model factory
│   │   ├── skills/                   # Skills management
│   │   ├── runtime/                  # Runtime engine (runs, streaming, persistence)
│   │   └── config/                   # Hierarchical configuration
│   └── app/
│       ├── gateway/                  # FastAPI REST API + authentication
│       └── channels/                 # IM platform integrations
├── frontend/
│   └── src/                          # Next.js 16 web interface
│       ├── core/                     # Business logic (API, threads, auth, i18n)
│       ├── components/workspace/     # Chat workspace UI
│       └── app/                      # Next.js App Router pages
├── skills/                           # Public agent skills catalog
├── docker/                           # Docker infrastructure
├── scripts/                          # Operational tooling
└── .github/workflows/                # CI/CD pipelines
```

## Architecture Overview

DeerFlow is a full-stack super agent harness built on LangGraph. The **backend-core**
(deerflow-harness package) provides the agent framework — a lead agent with a 20-middleware
chain, subagent delegation, sandbox execution, tool ecosystem, MCP integration, memory
system, and runtime engine. The **backend-gateway** exposes this via a FastAPI REST API
with JWT authentication and IM channel integrations (Feishu, Slack, Telegram, etc.).

The **frontend** is a Next.js 16 React application that communicates with the backend
via the LangGraph SDK and REST API. It supports both a full connected mode and a static
demo mode (`NEXT_PUBLIC_STATIC_WEBSITE_ONLY`).

The **skills** directory contains public agent skills (SKILL.md-based) organized by
functional category. The **platform** domain covers Docker deployment, CI/CD pipelines,
and operational scripts.

## Child Knowledge Nodes

### Domains

- **backend-core** — Navigate when: modifying agent orchestration, sandbox execution,
  tool ecosystem, memory, model integration, skills management, runtime engine, or
  configuration. Covers the deerflow-harness package with strict no-app-import boundary.
  Excludes: gateway API (see backend-gateway), frontend (see frontend).

- **backend-gateway** — Navigate when: modifying REST API routes, authentication/authorization,
  or IM channel integrations. Covers the FastAPI application layer on port 8001.
  Excludes: core agent logic (see backend-core), frontend (see frontend).

- **frontend** — Navigate when: modifying the Next.js web interface, chat workspace,
  message rendering, thread management, settings, i18n, or landing pages.
  Excludes: backend API (see backend-gateway), agent logic (see backend-core).

- **skills** — Navigate when: adding or modifying public agent skills, understanding
  skill structure and conventions, debugging skill loading or activation.
  Excludes: skills management in the harness (see backend-core/skills-management).

- **platform** — Navigate when: modifying Docker deployment, CI/CD pipelines, or
  operational scripts. Covers containerization, GitHub Actions, and setup tooling.

### Shared Components

- **backend-core/sandbox-execution** — Navigate when: adding sandbox providers, modifying
  sandbox tools, or debugging sandbox isolation issues. Used by agent orchestration,
  tool ecosystem, and subagent delegation.

- **backend-core/tool-ecosystem/mcp-integration** — Navigate when: adding MCP server
  support, modifying session pooling, or debugging tool discovery. Used by tool
  ecosystem, gateway API, and frontend.

- **backend-core/model-integration** — Navigate when: adding LLM provider support,
  modifying model factory, or debugging provider-specific patches. Used by agent
  orchestration, memory, summarization, and title generation.

- **backend-core/skills-management** — Navigate when: modifying skill discovery, loading,
  validation, or storage. Used by agent orchestration, gateway API, and frontend.

### Cross-Cutting Patterns

- **backend-core/configuration** — Navigate when: modifying config schema, adding config
  fields, or debugging config resolution. Cross-cuts backend-core, backend-gateway,
  and platform with YAML/env-var resolution and hot-reload.

- **backend-gateway/authentication** — Navigate when: modifying auth flow, adding auth
  providers, or debugging JWT/session issues. Cross-cuts gateway API, frontend, and
  channel integrations with auth-disabled mode branching.

## Overall Conventions

- **Strict package boundary**: The deerflow-harness package (`backend/packages/harness/deerflow/`)
  must never import from `backend/app/`. This boundary is enforced by CI.
- **Configuration**: YAML-based with environment variable override via `${VAR:default}`
  syntax. Hot-reload supported for most config sections; some require restart.
- **Frontend dual-mode**: All gateway-dependent code is gated behind `isStaticWebsiteOnly()`
  — when `NEXT_PUBLIC_STATIC_WEBSITE_ONLY=true`, the app uses stubbed clients and static data.
- **SSE streaming**: Both backend (runtime engine) and frontend (thread client) use
  Server-Sent Events for real-time streaming with heartbeat sentinels.
- **CSRF protection**: Double Submit Cookie pattern with `X-CSRF-Token` header required
  on all state-changing API methods.
- **Docker deployment**: Production uses docker-compose with Nginx reverse proxy on port
  2026; development uses docker-compose with hot-reload.

## Generation Metadata

- **Generated**: 2026-06-16T00:00:00+08:00
- **Scale**: L
- **Tree depth**: 3 levels (required range: 3–4)
- **Total nodes**: 46 (1 root + 5 domain + 23 intermediate + 17 leaf)
- **Total knowledge entries**: 1,067

### Node Distribution by Level

| Level | Count | Nodes |
|-------|-------|-------|
| 0 (root) | 1 | Root SKILL.md |
| 1 (domains) | 5 | backend-core, backend-gateway, frontend, skills, platform |
| 2 (subdomains) | 23 | agent-orchestration, sandbox-execution, tool-ecosystem, runtime-engine, configuration, memory-system, model-integration, skills-management, rest-api, authentication, channel-integrations, workspace-interface, core-services, settings-system, internationalization, landing-site, content-creation, data-analysis, research, development, docker-infrastructure, ci-cd, operational-scripts |
| 3 (leaf) | 17 | lead-agent, middleware-chain, subagent-delegation, run-management, streaming, state-persistence, local-sandbox, docker-sandbox, sandbox-tools, builtin-tools, community-tools, mcp-integration, chat-system, message-rendering, artifact-display, api-integration, thread-client |

### Entry Counts by Domain

| Domain | Entries |
|--------|---------|
| backend-core | 441 |
| frontend | 190 |
| platform | 121 |
| Root (overall conventions) | 119 |
| skills | 105 |
| backend-gateway | 91 |

### Entry Counts by Category

| Category | Entries |
|----------|---------|
| Gotchas | 265 |
| Architecture | 197 |
| Patterns | 158 |
| Dependencies | 147 |
| Decisions | 122 |
| Conventions | 106 |
| Emergent categories (Security Considerations, Branching Behavior, Provider-Specific Behavior, etc.) | 72 |

### Coverage Assessment

All 5 top-level source domains are covered:
- **backend-core** (`backend/packages/harness/deerflow/`): 8 subdomains covering agents, sandbox, tools, MCP, models, skills, runtime, config
- **backend-gateway** (`backend/app/gateway/`, `backend/app/channels/`): 3 subdomains covering REST API, authentication, channel integrations
- **frontend** (`frontend/src/`): 5 subdomains covering workspace UI, core services, settings, i18n, landing
- **skills** (`skills/public/`): 4 subdomains covering content creation, data analysis, research, development
- **platform** (`docker/`, `.github/workflows/`, `scripts/`): 3 subdomains covering Docker, CI/CD, operational scripts

### Component-Like Nodes

4 nodes identified as shared across 3+ domains with API Surface, Usage Examples, and Consumer Analysis:
- `backend-core/model-integration` — consumed by agent orchestration, memory, subagents, title/summarization middleware
- `backend-core/sandbox-execution` — consumed by agent orchestration, tool ecosystem, subagent delegation, memory
- `backend-core/skills-management` — consumed by agent orchestration, prompt template, skill activation middleware, summarization
- `backend-core/tool-ecosystem/mcp-integration` — consumed by tool ecosystem, agent orchestration, deferred tool search, runtime engine

### Cross-Cutting Nodes

2 nodes identified with Branching Table and Affected Scope:
- `backend-core/configuration` — 6-row branching table (memory/SQLite/PostgreSQL backends, local/Docker sandbox, thinking enabled/disabled); affects 9 modules
- `backend-gateway/authentication` — 3-row branching table (authenticated/auth-disabled/internal); affects 14 modules
