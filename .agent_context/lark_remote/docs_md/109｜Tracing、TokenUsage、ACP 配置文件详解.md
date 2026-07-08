<title>109｜Tracing、TokenUsage、ACP 配置文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| tracing_config.py | LangSmith/Langfuse 开关和 env fallback。 |
| token_usage_config.py | token usage display/tracking 开关。 |
| acp_config.py | ACP agent 外部执行配置。 |
| agents_api_config.py | 自定义 agents API 开关。 |
| skill_evolution_config.py | 任务结束后 skill 自演化提示开关。 |

```mermaid
flowchart TD
  ConfigYaml --> TracingConfig
  ConfigYaml --> TokenUsageConfig
  ConfigYaml --> ACPConfig
  ConfigYaml --> AgentsAPIConfig
  ConfigYaml --> SkillEvolutionConfig
  TracingConfig --> Callbacks[tracing callbacks]
  TokenUsageConfig --> TokenUsageMiddleware
  ACPConfig --> InvokeACPTool
  AgentsAPIConfig --> AgentsRouter
  SkillEvolutionConfig --> PromptSection
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