---
name: knowledge-backend-core-memory-system
description: >
  Covers the memory system: FileMemoryStorage with mtime-based cache, MemoryUpdater with
  sync LLM path, memory queue with per-agent isolation, message processing with correction/
  reinforcement signal detection, and summarization hook. Navigate when: debugging memory
  updates, modifying memory storage, adding memory backends, troubleshooting fact
  deduplication, or working on memory injection.
  Excludes: agent orchestration (see ../agent-orchestration/), configuration (see ../configuration/).
  Keywords: memory, FileMemoryStorage, MemoryUpdater, memory queue, MemoryMiddleware,
  memory_flush_hook, fact deduplication, correction detection, reinforcement detection,
  atomic write, mtime cache, per-agent isolation, confidence thresholding.
---

## Module Structure

The memory system captures, stores, and injects persistent facts about users across
conversations. It uses a pipeline: MemoryMiddleware queues messages → MemoryUpdater
processes with LLM → FileMemoryStorage persists with atomic writes. Memory is injected
into conversations via DynamicContextMiddleware.

### Directory Layout
- `backend/packages/harness/deerflow/agents/memory/__init__.py` — Public API: storage, queue, updater, prompt utilities
- `backend/packages/harness/deerflow/agents/memory/storage.py` — FileMemoryStorage with mtime-based cache, atomic writes
- `backend/packages/harness/deerflow/agents/memory/updater.py` — MemoryUpdater with sync LLM path, fact deduplication
- `backend/packages/harness/deerflow/agents/memory/message_processing.py` — Message filtering, correction/reinforcement detection
- `backend/packages/harness/deerflow/agents/memory/summarization_hook.py` — `memory_flush_hook` for summarization integration
- `backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py` — MemoryMiddleware for queue management
- `backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py` — Memory injection as system-reminder

### Key Entry Points
- `FileMemoryStorage` in `backend/packages/harness/deerflow/agents/memory/storage.py` — Main storage implementation
- `MemoryUpdater` in `backend/packages/harness/deerflow/agents/memory/updater.py` — LLM-based memory update processing
- `MemoryMiddleware` in `backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py` — Queue management middleware
- `memory_flush_hook` in `backend/packages/harness/deerflow/agents/memory/summarization_hook.py` — Flush memory before summarization

## Gotchas
- Memory updater uses a synchronous LLM path to avoid cross-loop connection reuse issues with async model clients (`backend/packages/harness/deerflow/agents/memory/updater.py`, `git:722c690f`)
- Memory queue is isolated by agent name to prevent cross-agent memory contamination — each agent has its own memory namespace (`backend/packages/harness/deerflow/agents/memory/updater.py`, `git:722c690f`)
- FileMemoryStorage uses atomic writes (temp file + replace) to prevent corruption on concurrent writes (`backend/packages/harness/deerflow/agents/memory/storage.py`)
- Correction and reinforcement signals are detected via regex patterns in both English and Chinese — missing a language pattern means signals in that language are silently ignored (`backend/packages/harness/deerflow/agents/memory/message_processing.py`)
- Memory is injected once per conversation as a frozen snapshot via DynamicContextMiddleware — subsequent turns do not re-inject unless the date changes (`backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`)

## Architecture
- Pipeline: MemoryMiddleware queues conversation turns → MemoryUpdater processes queue with LLM → FileMemoryStorage persists facts with atomic writes → DynamicContextMiddleware injects memory into new conversations (`backend/packages/harness/deerflow/agents/memory/`)
- Fact deduplication: MemoryUpdater compares new facts against existing facts and merges or replaces based on confidence scoring (`backend/packages/harness/deerflow/agents/memory/updater.py`)
- Storage is pluggable: `FileMemoryStorage` is the default, but the storage class can be swapped via config (`backend/packages/harness/deerflow/agents/memory/storage.py`)
- Memory is scoped per-user and per-agent: storage paths include both user_id and agent_name (`backend/packages/harness/deerflow/agents/memory/storage.py`)

## Decisions
- Synchronous LLM path was chosen for memory updates to avoid cross-loop connection reuse issues — async model clients can have event-loop conflicts when used from background tasks (`backend/packages/harness/deerflow/agents/memory/updater.py`, `git:722c690f`)
- Memory queue isolation by agent name prevents cross-agent memory contamination when multiple custom agents share a process (`backend/packages/harness/deerflow/agents/memory/updater.py`, `git:722c690f`)
- Atomic writes (temp file + os.replace) were chosen over direct file writes to prevent corruption from concurrent access (`backend/packages/harness/deerflow/agents/memory/storage.py`)

## Patterns
- Storage uses mtime-based caching: memory files are re-read only if the file modification time has changed since last read (`backend/packages/harness/deerflow/agents/memory/storage.py`)
- Message processing filters out upload blocks and detects correction/reinforcement signals via regex (`backend/packages/harness/deerflow/agents/memory/message_processing.py`)
- Memory injection uses a frozen-snapshot pattern: memory is read once at conversation start and injected as a dedicated HumanMessage (`backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`)

## Conventions
- Memory files are stored as JSON in per-user directories under the configured memory path (`backend/packages/harness/deerflow/agents/memory/storage.py`)
- Fact entries include content, confidence score, and source metadata (`backend/packages/harness/deerflow/agents/memory/updater.py`)
- Memory queue is a simple list in graph state, processed by MemoryUpdater after each conversation turn (`backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py`)

## Dependencies
- LangChain for LLM model creation in MemoryUpdater (`backend/packages/harness/deerflow/agents/memory/updater.py`)
- `deerflow.models.create_chat_model` for memory processing model (`backend/packages/harness/deerflow/agents/memory/updater.py`)
- `deerflow.config.app_config` for memory configuration (enabled, storage path, injection settings) (`backend/packages/harness/deerflow/agents/memory/`)
