---
name: knowledge-backend-core-runtime-engine-streaming
description: >
  Covers streaming: StreamBridge ABC with publish/subscribe/cleanup, StreamEvent dataclass,
  HEARTBEAT_SENTINEL and END_SENTINEL, MemoryStreamBridge implementation, async provider,
  and SSE compatibility. Navigate when: modifying streaming behavior, adding stream
  backends, debugging SSE issues, or working on heartbeat/keepalive.
  Excludes: run management (see ../run-management/), state persistence (see ../state-persistence/).
  Keywords: StreamBridge, StreamEvent, SSE, heartbeat, HEARTBEAT_SENTINEL, END_SENTINEL,
  publish, subscribe, AsyncIterator, Last-Event-ID, MemoryStreamBridge, stream_bridge,
  async_provider, pub/sub.
---

## Module Structure

The streaming system decouples agent workers (producers) from SSE endpoints (consumers)
using a pub/sub pattern. It supports heartbeat keepalive, last-event-ID reconnection,
and clean producer-consumer lifecycle management.

### Directory Layout
- `backend/packages/harness/deerflow/runtime/stream_bridge/__init__.py` — Public API exports
- `backend/packages/harness/deerflow/runtime/stream_bridge/base.py` — StreamBridge ABC, StreamEvent, sentinels
- `backend/packages/harness/deerflow/runtime/stream_bridge/memory.py` — In-memory StreamBridge implementation
- `backend/packages/harness/deerflow/runtime/stream_bridge/async_provider.py` — Async provider for stream bridge

### Key Entry Points
- `StreamBridge` ABC in `backend/packages/harness/deerflow/runtime/stream_bridge/base.py` — Abstract streaming interface
- `StreamEvent` in `backend/packages/harness/deerflow/runtime/stream_bridge/base.py` — Event dataclass
- `HEARTBEAT_SENTINEL` / `END_SENTINEL` in `backend/packages/harness/deerflow/runtime/stream_bridge/base.py` — Special sentinel events
- `MemoryStreamBridge` in `backend/packages/harness/deerflow/runtime/stream_bridge/memory.py` — Default in-memory implementation

## Gotchas
- `HEARTBEAT_SENTINEL` is yielded every 15 seconds when no events arrive — SSE clients use this to detect connection liveness (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- `END_SENTINEL` signals that no more events will be produced — consumers must close the connection after receiving it (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- StreamEvent.id is monotonically increasing and supports `Last-Event-ID` reconnection — clients can resume from where they disconnected (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- `cleanup()` supports an optional delay to give late subscribers a chance to drain remaining events before resources are released (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- StreamBridge is an ABC — all implementations must provide `publish`, `publish_end`, `subscribe`, and `cleanup` methods (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)

## Architecture
- Pub/sub pattern: agent workers call `publish(run_id, event, data)` to enqueue events; SSE endpoints call `subscribe(run_id)` to get an async iterator (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Event flow: worker produces events → bridge queues them by run_id → subscriber consumes via async iterator → `END_SENTINEL` terminates the stream (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Heartbeat: when no events arrive within `heartbeat_interval` (default 15s), the bridge yields `HEARTBEAT_SENTINEL` to keep the SSE connection alive (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- MemoryStreamBridge uses asyncio.Queue per run_id for event buffering (`backend/packages/harness/deerflow/runtime/stream_bridge/memory.py`)

## Decisions
- StreamBridge was designed as an ABC to allow swapping implementations (in-memory, Redis, Kafka) without changing producer/consumer code (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Heartbeat interval of 15 seconds was chosen as a balance between connection liveness detection and network overhead (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- `Last-Event-ID` support was added for SSE reconnection — clients can resume streaming after temporary disconnects (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)

## Patterns
- Producer: `await bridge.publish(run_id, "updates", data)` → `await bridge.publish_end(run_id)` (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Consumer: `async for event in bridge.subscribe(run_id, last_event_id="42"): process(event)` (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Cleanup: `await bridge.cleanup(run_id, delay=300)` — waits 5 minutes before releasing resources (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)

## Conventions
- Event names follow SSE conventions: `metadata`, `updates`, `events`, `error`, `end` (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Event data is JSON-serializable (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Run ID is the namespace key for event queues (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)

## Dependencies
- asyncio for Queue-based event buffering (`backend/packages/harness/deerflow/runtime/stream_bridge/memory.py`)
- Python abc for abstract base class definition (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
