{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>78｜Tavily、Firecrawl、Exa、Serper Web Search Provider 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清各 web_search/web_fetch provider 的接入方式。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Tavily | TavilyClient，web_search 和 web_fetch。 |\n| Firecrawl | FirecrawlApp，搜索和页面抓取。 |\n| Exa | Exa SDK，搜索结果和页面内容。 |\n| Serper | Google Serper API，max_results。 |\n| 接入点 | 配置工具组后进入 get_available_tools。 |\n\n```mermaid\nflowchart TD\n  Agent[agent tool call web_search] --> Tool[get_available_tools selected provider]\n  Tool --> Key[read provider API key]\n  Key --> Client[provider client]\n  Client --> API[external search API]\n  API --> Normalize[normalize markdown/text result]\n  Normalize --> ToolMessage[return ToolMessage]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "TBw5dOi4Pop0pcxsIK2mNW9Fyqe",
      "revision_id": 18
    }
  }
}
