<title>206｜Event Store / History Specs/Plans 详解</title>

<callout emoji="✅">
**本章目标：**继续拆单测试族、单规格文档和根文档模块。
</callout>

| 模块点 | 说明 |
|-|-|
| 2026-04-10-event-store-history.md | event store history plan。 |
| 2026-04-11-runjournal-history-evaluation.md | RunJournal history evaluation。 |
| 目标 | run history/event store 可观测性。 |
| 关联 | runtime/journal、run_event_store、frontend history。 |

```mermaid
flowchart TD
  Need[history visibility] --> Plan[event store history]
  Plan --> RunJournal[RunJournal]
  RunJournal --> EventStore[RunEventStore]
  EventStore --> API[run messages/events API]
  API --> Frontend[thread history UI]
  Evaluation --> Improvements
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart LR
  F["make_run_event_store"] --> ES["RunEventStore"]
  ES --> MEM["MemoryRunEventStore"]
  ES --> DB["DbRunEventStore"]
  ES --> JSONL["JsonlRunEventStore"]
  CB["LangChain callbacks"] --> J["RunJournal._put"]
  J --> BUF["event buffer"]
  BUF -->|"threshold"| FB["_flush_sync"]
  FB --> PB["put_batch"]
  PB --> ES
  RM["GET thread messages"] --> LM["list_messages"]
  RR["GET run messages"] --> LMR["list_messages_by_run"]
  RE["GET run events"] --> LE["list_events"]
  LM --> ES
  LMR --> ES
  LE --> ES
```