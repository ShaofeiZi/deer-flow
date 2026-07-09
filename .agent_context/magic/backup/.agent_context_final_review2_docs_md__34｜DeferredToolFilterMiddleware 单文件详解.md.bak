<title>34｜DeferredToolFilterMiddleware 单文件详解</title>

<callout emoji="✅">
**本章目标：**讲清 tool_search 开启时，部分工具如何先隐藏、再按需提升，降低模型工具 schema 压力。
</callout>

| 概念 | 说明 |
|-|-|
| deferred_names | 暂不暴露给模型的工具名集合。 |
| promoted | state.promoted.names 中已经被 tool_search 提升的工具。 |
| wrap_model_call | 只把 active tools 传给模型。 |
| wrap_tool_call | 如果模型调用未提升的 deferred tool，返回 blocked ToolMessage。 |

```mermaid
flowchart TD
  A[model request] --> B[all tools]
  B --> C[deferred_names]
  C --> D[promoted from state]
  D --> E[active tools = all minus hidden]
  E --> F[model sees active tools]
  F --> G{tool call deferred but not promoted?}
  G -->|yes| H[blocked ToolMessage]
  G -->|no| I[execute tool]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |
| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |
| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |
| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |

```mermaid
flowchart TD
  A[设计目的] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```
