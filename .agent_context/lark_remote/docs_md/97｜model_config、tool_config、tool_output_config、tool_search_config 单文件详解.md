<title>97｜model_config、tool_config、tool_output_config、tool_search_config 单文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| model_config | 定义模型 provider、model name、API 参数和能力开关。 |
| tool_config | 定义工具组和启用策略。 |
| tool_output_config | 定义工具输出预算阈值和外置策略。 |
| tool_search_config | 控制 deferred tool search。 |

```mermaid
flowchart TD
  ConfigYaml --> ModelConfig
  ConfigYaml --> ToolConfig
  ConfigYaml --> ToolOutputConfig
  ConfigYaml --> ToolSearchConfig
  ModelConfig --> ModelFactory
  ToolConfig --> AvailableTools
  ToolOutputConfig --> ToolOutputBudgetMiddleware
  ToolSearchConfig --> DeferredToolFilterMiddleware
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块承担 agent 扩展能力，是为了把工具、知识、长期上下文或执行环境做成可组合部件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可扩展、可配置、可替换。 |
| 代价 | 代价是配置、prompt、工具 schema、外部服务任一环节出错都会影响结果。 |
| 重点代码 | 重点代码在 `backend/packages/harness/deerflow` 下对应 skills/mcp/memory/sandbox/tools/models 模块。 |
| 阅读路径 | 阅读路径：明确它给 agent 增加了什么能力，以及该能力在哪里被注入。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```