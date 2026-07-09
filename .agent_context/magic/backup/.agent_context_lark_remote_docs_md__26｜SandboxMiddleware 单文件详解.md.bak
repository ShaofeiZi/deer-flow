<title>26｜SandboxMiddleware 单文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲清 sandbox 的懒加载、工具调用包裹和 sandbox_id 持久化。
</callout>

| Hook | 职责 |
|-|-|
| `before_agent/abefore_agent` | 非 lazy 模式提前 acquire sandbox。 |
| `wrap_tool_call/awrap_tool_call` | 工具调用前后检查 runtime.state.sandbox，新增时返回 Command(update)。 |
| `after_agent/aafter_agent` | 释放 sandbox。 |

```mermaid
flowchart TD
  A[tool call] --> B[read previous sandbox_id]
  B --> C[handler executes tool]
  C --> D[tool ensure_sandbox_initialized may mutate runtime.state]
  D --> E{new sandbox_id appeared?}
  E -->|no| F[return original result]
  E -->|yes| G[wrap ToolMessage or merge Command update]
  G --> H[persist sandbox.sandbox_id in graph state]
```

关键点：直接修改 runtime.state 不会自动进入 LangGraph reducer，所以 middleware 必须把新 sandbox_id 包进 Command(update)。

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
  A[设计动机] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[理解方式]
```