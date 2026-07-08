{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>83｜Exa 与 Serper Provider 单模块详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**细化 Exa 和 Serper 搜索 provider。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Exa | `_get_exa_client` 创建 Exa SDK client。 |\n| Exa search/fetch | 支持 web_search_tool 和 web_fetch_tool。 |\n| Serper | 读取 Serper API key，调用 Google Serper 搜索。 |\n| max_results | Serper 支持 max_results 控制。 |\n\n```mermaid\nflowchart TD\n  Query[search query or url] --> Provider{Exa or Serper}\n  Provider --> ExaClient[Exa client]\n  Provider --> SerperAPI[Serper HTTP API]\n  ExaClient --> ExaResult[search or fetch result]\n  SerperAPI --> SerperResult[organic results]\n  ExaResult --> Normalize[normalize markdown text]\n  SerperResult --> Normalize\n  Normalize --> ToolMessage\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "SXAvdVOyRo74WVxtEEOmZiivy7b",
      "revision_id": 18
    }
  }
}
