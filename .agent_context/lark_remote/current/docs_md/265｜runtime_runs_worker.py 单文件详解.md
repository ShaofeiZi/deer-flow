# 265｜runtime/runs/worker.py 单文件详解

<callout emoji="✅">
**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。
</callout>

## 本轮源码校准补充：run_agent worker

```mermaid
flowchart TD
  Start[run_agent] --> Status[set running]
  Status --> Metadata[publish metadata]
  Metadata --> Runtime[build Runtime context]
  Runtime --> Agent[agent_factory -> graph]
  Agent --> Astream[agent.astream]
  Astream --> Publish[publish events to StreamBridge]
  Publish --> Complete[status/title/journal cleanup]
```

| 步骤 | 说明 |
|-|-|
| runtime context | 总是包含 `thread_id`、`run_id`，并合并 caller context 和 app_config。 |
| stream mode | `events` 目前不通过 Gateway 支持；values/messages/custom 等会被映射。 |
| rollback | 运行前会尽力捕获 checkpoint，便于 rollback 策略恢复。 |
| cleanup | 完成后 flush journal、更新状态/标题，并调度 stream bridge cleanup。 |

| 模块点 | 说明 |
|-|-|
| run_agent | 后台执行 agent graph。 |
| Runtime context | 注入 run_id/thread_id/store/checkpointer。 |
| astream | 消费 LangGraph stream chunks。 |
| rollback | 支持 pre-run checkpoint rollback。 |
| finalize | flush journal、更新 run/thread status、publish_end。 |

```mermaid
sequenceDiagram
  participant S as start_run
  participant W as run_agent
  participant A as agent_factory
  participant G as graph astream
  participant B as StreamBridge
  S->>W: create task
  W->>A: make lead agent
  A-->>W: graph
  W->>G: astream
  G-->>W: chunks
  W->>B: publish events
  W->>W: finalize status journal title
  W->>B: publish end
```