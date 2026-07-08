<title>254｜Runtime UserContext、Converters、Serialization 详解</title>

<callout emoji="✅">
**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。
</callout>

| 模块点 | 说明 |
|-|-|
| runtime/user_context.py | 当前用户上下文 ContextVar。 |
| runtime/converters.py | LangGraph/LangChain 转换。 |
| runtime/serialization.py | 消息和 state 序列化。 |
| runtime/runs/naming.py | run name。 |
| runtime/runs/schemas.py | RunStatus/DisconnectMode。 |

```mermaid
flowchart TD
  AuthMiddleware --> UserContext
  UserContext --> Paths
  UserContext --> RunConfig
  LangChainObjects --> Converters
  Converters --> Serialization
  Serialization --> APIResponse
  RunConfig --> Naming
  RunStatus --> Schemas
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```