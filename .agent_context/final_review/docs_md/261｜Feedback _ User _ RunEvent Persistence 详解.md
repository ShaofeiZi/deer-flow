<title>261｜Feedback / User / RunEvent Persistence 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 persistence/runtime 单文件，说明模型、仓储、provider 的调用关系。
</callout>

| 模块点 | 说明 |
|-|-|
| feedback/model.py | FeedbackRow。 |
| feedback/sql.py | FeedbackRepository。 |
| user/model.py | UserRow。 |
| models/run_event.py | RunEventRow。 |
| events store | RunJournal 写入 RunEventStore；只有 `run_events.backend=db` 时才落 `RunEventRow`。 |

```mermaid
flowchart TD
  FeedbackRouter --> FeedbackRepository
  FeedbackRepository --> FeedbackRow
  AuthProvider --> UserRow
  RunJournal --> RunEventStore
  RunEventStore --> MemoryOrJsonl[memory or jsonl backend]
  RunEventStore --> DbBackend[db backend]
  DbBackend --> RunEventRow
  RunsAPI --> RunEventStore
  FeedbackStats --> FeedbackRepository
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |
| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |
| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |
| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```