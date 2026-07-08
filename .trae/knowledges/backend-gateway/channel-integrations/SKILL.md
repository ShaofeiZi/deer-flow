---
name: knowledge-backend-gateway-channel-integrations
description: >
  Covers IM channel integrations: Channel base class, ChannelManager dispatcher, ChannelService
  lifecycle, MessageBus pub/sub, ChannelStore persistence, and platform-specific implementations
  (Feishu, Slack, Telegram, Discord, DingTalk, WeChat, WeCom).
  Navigate when: adding a new IM platform, debugging channel message delivery, modifying channel
  dispatch logic, troubleshooting WebSocket connections, adding channel commands, handling file
  uploads from IM platforms, configuring channel sessions.
  Excludes: HTTP API for channel management (see ../rest-api/), authentication (see ../authentication/).
  Keywords: channels, IM, Feishu, Slack, Telegram, Discord, DingTalk, WeChat, WeCom, ChannelManager,
  MessageBus, ChannelService, ChannelStore, WebSocket, inbound, outbound, streaming, slash commands.
---

## Module Structure

The channel integration system connects external IM platforms to the DeerFlow agent. It uses a
pluggable architecture: each platform implements the `Channel` ABC, messages flow through an async
`MessageBus` pub/sub hub, and the `ChannelManager` dispatches inbound messages to the LangGraph agent
via the Gateway's internal API.

### Directory Layout
- `backend/app/channels/__init__.py` — Public channel module exports
- `backend/app/channels/base.py` — Channel ABC: start/stop/send/send_file/receive_file lifecycle
- `backend/app/channels/manager.py` — ChannelManager: dispatch loop, chat/command handling, streaming, file ingestion
- `backend/app/channels/service.py` — ChannelService: singleton lifecycle, channel registry, start/stop/restart
- `backend/app/channels/message_bus.py` — MessageBus: async pub/sub, InboundMessage/OutboundMessage dataclasses
- `backend/app/channels/store.py` — ChannelStore: JSON-file-backed IM chat→DeerFlow thread mapping
- `backend/app/channels/commands.py` — Shared channel command definitions (/bootstrap, /new, /status, /models, /memory, /help)
- `backend/app/channels/feishu.py` — Feishu/Lark channel via WebSocket (lark-oapi)
- `backend/app/channels/slack.py` — Slack channel via Socket Mode (slack-sdk)
- `backend/app/channels/telegram.py` — Telegram channel via long polling
- `backend/app/channels/discord.py` — Discord channel
- `backend/app/channels/dingtalk.py` — DingTalk channel
- `backend/app/channels/wechat.py` — WeChat channel
- `backend/app/channels/wecom.py` — WeCom channel

### Key Entry Points
- `ChannelManager._dispatch_loop()` in `backend/app/channels/manager.py` — Main message dispatch loop
- `ChannelManager._handle_chat()` in `backend/app/channels/manager.py` — Chat message processing pipeline
- `ChannelService.start()` in `backend/app/channels/service.py` — Start all enabled channels
- `start_channel_service()` in `backend/app/channels/service.py` — Global singleton bootstrap

## Gotchas
- Channel shutdown can stall indefinitely (e.g. Feishu WebSocket waiting for ack), causing the gateway worker to hang under `uvicorn --reload` — the lifespan now wraps `stop_channel_service()` in `asyncio.wait_for(timeout=5.0)` (`backend/app/gateway/app.py`, `git:4e724101`)
- The ChannelManager communicates with the Gateway via `langgraph-sdk` using internal auth headers (`X-DeerFlow-Internal-Token` + CSRF cookie) — if the internal token is auto-generated (no `DEER_FLOW_INTERNAL_AUTH_TOKEN` env var), cross-process calls will fail because each worker gets a different token (`backend/app/channels/manager.py`, `backend/app/gateway/internal_auth.py`)
- `ChannelStore` is a simple JSON file with atomic rewrite on every mutation — under high concurrency, writes can be lost if two mutations race; this is acceptable for dev but needs a database backend for production (`backend/app/channels/store.py`)
- Channel config keys that indicate credentials are checked even when the channel is disabled — a warning is logged if credentials exist but `enabled: false`, helping operators catch misconfiguration (`backend/app/channels/service.py`, `git:9dc25987`)
- Streaming channels (Feishu, WeCom) use `runs.stream` with `stream_mode=["messages-tuple", "values"]` and throttle updates at 350ms minimum interval — non-streaming channels use `runs.wait` which blocks until completion (`backend/app/channels/manager.py`)
- File ingestion from IM platforms uses channel-specific readers registered in `INBOUND_FILE_READERS` — WeCom files require AES decryption via `aibot.crypto_utils.decrypt_file`, WeChat files may come from local paths or HTTP URLs (`backend/app/channels/manager.py`)
- `_resolve_attachments()` only allows artifact paths under `/mnt/user-data/outputs/` — any other virtual path is rejected to prevent exfiltrating uploads or workspace files via IM channels (`backend/app/channels/manager.py`)
- Slack `allowed_users` accepts a single string, a list, or other scalar types — non-list/non-string values are treated as a single string with a warning (`backend/app/channels/slack.py`, `git:410f0c48`)

## Architecture
- Pluggable channel system: each platform implements `Channel` ABC (start/stop/send) and is registered in `_CHANNEL_REGISTRY` dict mapping name → import path (`backend/app/channels/service.py`)
- Message flow: Platform → Channel.start() → MessageBus.publish_inbound() → ChannelManager._dispatch_loop() → _handle_chat() → langgraph-sdk API → MessageBus.publish_outbound() → Channel._on_outbound() → Platform (`backend/app/channels/manager.py`, `backend/app/channels/base.py`)
- ChannelManager uses `langgraph-sdk` async client to communicate with Gateway's LangGraph-compatible API — it creates threads, sends runs, and receives responses through the same API as the web frontend (`backend/app/channels/manager.py`)
- Session config layering: DEFAULT_RUN_CONTEXT → default_session → channel_session → user_session — each layer overrides the previous, enabling per-channel and per-user customization (`backend/app/channels/manager.py`)
- Custom agents in channels are implemented as `lead_agent` + `agent_name` context injection — `assistant_id` values other than "lead_agent" are normalized and injected as `agent_name` in run_context (`backend/app/channels/manager.py`)

## Decisions
- Chose `langgraph-sdk` client over direct LangGraph API calls — enables channel manager to use the same auth, CSRF, and routing as web clients (`backend/app/channels/manager.py`)
- Chose JSON file store for channel→thread mapping over SQL — simplicity for single-instance deployments; the store interface is swappable (`backend/app/channels/store.py`)
- Chose `multitask_strategy="reject"` for channel runs — prevents concurrent runs on the same thread, returning "This conversation is already processing" message (`backend/app/channels/manager.py`)
- Chose 350ms minimum interval for streaming updates — balances responsiveness with rate limiting on IM platform APIs (`backend/app/channels/manager.py`)

## Patterns
- Channel implementations use `_make_inbound()` factory for creating `InboundMessage` instances with consistent defaults (`backend/app/channels/base.py`)
- `_on_outbound()` callback filters by `channel_name` and sends text first, then uploads file attachments — file uploads are skipped entirely when text send fails to avoid partial deliveries (`backend/app/channels/base.py`)
- `receive_file()` is a hook method on `Channel` ABC with default no-op — only FeishuChannel overrides it to download files from Feishu messages and inject sandbox paths into msg.text (`backend/app/channels/base.py`, `backend/app/channels/feishu.py`)
- Slash-skill commands (e.g. `/my-skill do something`) are resolved via `parse_slash_skill_reference()` and routed as chat messages with the skill name preserved in the text (`backend/app/channels/manager.py`)
- `_extract_response_text()` walks messages backwards from the end, stopping at the last human message — handles AI text, clarification interrupts, and content blocks (`backend/app/channels/manager.py`)

## Conventions
- Channel config keys are documented in each channel class docstring (`backend/app/channels/feishu.py`, `backend/app/channels/slack.py`)
- `CHANNEL_CAPABILITIES` dict declares which channels support streaming — used as fallback when the live channel instance is unavailable (`backend/app/channels/manager.py`)
- `KNOWN_CHANNEL_COMMANDS` is a single `frozenset` shared across all channel parsers and the manager dispatcher — adding a command is a one-line edit (`backend/app/channels/commands.py`)
- All channel implementations use `logger = logging.getLogger(__name__)` at module level (`backend/app/channels/`)

## Dependencies
- Feishu: `lark-oapi` for WebSocket client and API calls (`backend/app/channels/feishu.py`)
- Slack: `slack-sdk` for Socket Mode and Web API, `markdown_to_mrkdwn` for Markdown→Slack mrkdwn conversion (`backend/app/channels/slack.py`)
- WeCom: `aibot.crypto_utils.decrypt_file` for AES file decryption (`backend/app/channels/manager.py`)
- All channels: `langgraph-sdk` for Gateway API communication, `httpx` for HTTP file downloads (`backend/app/channels/manager.py`)

## Channel Capabilities
- Feishu and WeCom support streaming responses (real-time text updates via `runs.stream`) (`backend/app/channels/manager.py`)
- Slack, Telegram, Discord, DingTalk, and WeChat use non-streaming mode (`runs.wait` blocks until completion) (`backend/app/channels/manager.py`)
- Feishu supports file receive (downloads images/documents from messages, saves to sandbox) (`backend/app/channels/feishu.py`)
- Slack supports `allowed_users` filtering and bot mention stripping (`backend/app/channels/slack.py`)

## Error Handling & Recovery
- `ChannelManager._handle_message()` catches `InvalidChannelSessionConfigError` and `SlashSkillCommandResolutionError` separately, sending specific error messages to the user — generic exceptions send "An internal error occurred" (`backend/app/channels/manager.py`)
- Thread-busy errors (concurrent run rejected) return a user-friendly "already processing" message instead of a generic error (`backend/app/channels/manager.py`)
- Streaming error recovery: if `runs.stream` raises, the finally block extracts the last known values snapshot or falls back to a synthetic AI message with accumulated text (`backend/app/channels/manager.py`)
- `ChannelService.restart_channel()` stops the existing instance, removes it, and creates a fresh one — used by the `/api/channels/{name}/restart` endpoint (`backend/app/channels/service.py`)
