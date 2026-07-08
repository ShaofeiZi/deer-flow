<title>265｜runtime/runs/worker.py 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。
</callout>

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

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统中抽出来。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是学习和定位更聚焦。 |
| 代价 | 代价是章节数量更多，需要依赖目录维护。 |
| 重点代码 | 重点代码见本章列出的文件路径。 |
| 阅读路径 | 阅读路径：先看上游输入和下游输出，再读关键函数。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```