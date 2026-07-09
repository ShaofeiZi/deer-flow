<title>269｜subagents registry/config/status/token_collector 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| registry.py | 获取 built-in/custom subagent config。 |
| config.py | SubagentConfig 和模型解析。 |
| status_contract.py | 结果 additional_kwargs 标准。 |
| token_collector.py | 收集子代理 token usage。 |
| builtins | general-purpose、bash。 |

```mermaid
flowchart TD
  AppConfig --> Registry
  Registry --> Builtins[general purpose bash]
  Registry --> Custom[custom subagents]
  Config --> ModelResolve[resolve subagent model]
  Executor --> TokenCollector
  Executor --> StatusContract
  StatusContract --> FrontendSubtaskCard
  TokenCollector --> UsageRecords
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