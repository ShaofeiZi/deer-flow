---
name: knowledge-backend-core-tool-ecosystem-community-tools
description: >
  Covers community tool integrations: ddg_search (DuckDuckGo), exa, firecrawl, serper,
  tavily, jina_ai, image_search, and infoquest. Navigate when: adding a new community
  tool provider, debugging API integration issues, configuring provider API keys, or
  understanding community tool patterns.
  Excludes: builtin tools (see ../builtin-tools/), MCP integration (see ../mcp-integration/).
  Keywords: community tools, ddg_search, DuckDuckGo, exa, firecrawl, serper, tavily,
  jina_ai, image_search, infoquest, web search, API integration, provider pattern.
---

## Module Structure

Community tools integrate third-party APIs (web search, content extraction, image search)
as agent-callable tools. Each provider lives in its own package under `community/` and
follows a consistent pattern: a `tools.py` module exporting the tool function(s).

### Directory Layout
- `backend/packages/harness/deerflow/community/ddg_search/tools.py` — DuckDuckGo web search
- `backend/packages/harness/deerflow/community/exa/tools.py` — Exa AI search
- `backend/packages/harness/deerflow/community/firecrawl/tools.py` — Firecrawl web scraping
- `backend/packages/harness/deerflow/community/serper/tools.py` — Serper Google search API
- `backend/packages/harness/deerflow/community/tavily/tools.py` — Tavily AI search
- `backend/packages/harness/deerflow/community/jina_ai/tools.py` — Jina AI content extraction
- `backend/packages/harness/deerflow/community/jina_ai/jina_client.py` — Jina AI HTTP client
- `backend/packages/harness/deerflow/community/image_search/tools.py` — Image search integration
- `backend/packages/harness/deerflow/community/infoquest/tools.py` — InfoQuest search
- `backend/packages/harness/deerflow/community/infoquest/infoquest_client.py` — InfoQuest HTTP client

### Key Entry Points
- Each provider's `tools.py` exports the tool function(s) — imported by `get_available_tools()`
- Provider-specific clients (e.g., `jina_client.py`, `infoquest_client.py`) handle API communication

## Gotchas
- Community tools require API keys configured in the app config — tools silently fail or return errors if keys are missing (`backend/packages/harness/deerflow/community/`)
- Some providers (jina_ai, infoquest) have dedicated HTTP client modules separate from the tool definition — API changes may need updates in both files (`backend/packages/harness/deerflow/community/jina_ai/`, `backend/packages/harness/deerflow/community/infoquest/`)
- Community tools are loaded via config-defined tool groups — a tool not listed in any group will not be available to agents (`backend/packages/harness/deerflow/tools/tools.py`)
- Provider rate limits are not handled by DeerFlow — the tool will return the provider's error response directly to the agent (`backend/packages/harness/deerflow/community/`)

## Architecture
- Each community provider is a self-contained package with its own `tools.py` exporting tool functions (`backend/packages/harness/deerflow/community/`)
- Tools are registered in the app config under tool groups and loaded by `get_available_tools()` based on the agent's configured groups (`backend/packages/harness/deerflow/tools/tools.py`)
- Some providers include dedicated HTTP client modules (jina_ai, infoquest) for API communication, separating concerns from tool logic (`backend/packages/harness/deerflow/community/jina_ai/jina_client.py`)

## Decisions
- Community tools are organized by provider rather than by function to keep each integration self-contained and easy to add/remove (`backend/packages/harness/deerflow/community/`)
- Provider-specific HTTP clients are separated from tool definitions to allow reuse and independent testing (`backend/packages/harness/deerflow/community/jina_ai/`, `backend/packages/harness/deerflow/community/infoquest/`)

## Patterns
- Each provider package has an `__init__.py` and a `tools.py` — the tool function is the public API (`backend/packages/harness/deerflow/community/`)
- Tool functions use `@tool` decorator with standard parameter patterns (query, max_results, etc.) (`backend/packages/harness/deerflow/community/`)
- API clients use a simple request/response pattern with error handling returning structured results (`backend/packages/harness/deerflow/community/jina_ai/jina_client.py`)

## Conventions
- Provider package names are lowercase with underscores: `ddg_search`, `jina_ai`, `image_search` (`backend/packages/harness/deerflow/community/`)
- Tool names are descriptive: `ddg_search`, `exa_search`, `firecrawl_scrape`, `serper_search`, `tavily_search` (`backend/packages/harness/deerflow/community/`)
- API keys are read from app config, not environment variables directly (`backend/packages/harness/deerflow/community/`)

## Dependencies
- Provider-specific SDKs or HTTP clients as needed (e.g., `httpx` for API calls) (`backend/packages/harness/deerflow/community/`)
- LangChain `@tool` decorator for tool registration (`backend/packages/harness/deerflow/community/`)
- `deerflow.config.app_config` for API key and configuration access (`backend/packages/harness/deerflow/community/`)
