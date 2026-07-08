<title>92｜Subagents、Summarization、Title、Tracing Config 详解</title>

<callout emoji="✅">
**本章目标：**拆 agent 行为增强相关配置。
</callout>

| 模块点 | 说明 |
|-|-|
| SubagentsAppConfig | 内置 subagent override 和 custom subagent。 |
| SummarizationConfig | 摘要触发、保留策略、技能保留。 |
| TitleConfig | 标题生成开关、模型、prompt、长度。 |
| TracingConfig | LangSmith/Langfuse 开关和环境变量。 |
| TokenUsageConfig | token usage 展示和统计开关。 |

```mermaid
flowchart TD
  Config[config yaml] --> Sub[Subagents config]
  Config --> Sum[Summarization config]
  Config --> Title[Title config]
  Config --> Trace[Tracing config]
  Config --> Token[Token usage config]
  Sub --> Registry[subagent registry]
  Sum --> SummaryMW[SummarizationMiddleware]
  Title --> TitleMW[TitleMiddleware]
  Trace --> Callbacks[tracing callbacks]
  Token --> TokenMW[TokenUsageMiddleware]
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