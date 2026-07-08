<title>83｜Exa 与 Serper Provider 单模块详解</title>

<callout emoji="✅">
**本章目标：**细化 Exa 和 Serper 搜索 provider。
</callout>

| 模块点 | 说明 |
|-|-|
| Exa | `_get_exa_client` 创建 Exa SDK client。 |
| Exa search/fetch | 支持 web_search_tool 和 web_fetch_tool。 |
| Serper | 读取 Serper API key，调用 Google Serper 搜索。 |
| max_results | Serper 支持 max_results 控制。 |

```mermaid
flowchart TD
  Query[search query or url] --> Provider{Exa or Serper}
  Provider --> ExaClient[Exa client]
  Provider --> SerperAPI[Serper HTTP API]
  ExaClient --> ExaResult[search or fetch result]
  SerperAPI --> SerperResult[organic results]
  ExaResult --> Normalize[normalize markdown text]
  SerperResult --> Normalize
  Normalize --> ToolMessage
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