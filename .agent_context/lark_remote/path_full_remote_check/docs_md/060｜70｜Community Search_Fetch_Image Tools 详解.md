{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>70｜Community Search/Fetch/Image Tools 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 Tavily、Firecrawl、Exa、Jina、DDG、InfoQuest、Serper 等社区工具如何接入。\n</callout>\n\n# 1. 模块职责\n\n| 模块 | 说明 |\n|-|-|\n| Tavily | web_search/web_fetch，TAVILY_API_KEY。 |\n| Firecrawl | web_search/web_fetch，FirecrawlApp。 |\n| Exa | 搜索和抓取网页。 |\n| Jina AI | 异步 web_fetch，支持 proxy/timeout。 |\n| DDG Search | 文本搜索，区域和 Wikipedia 后端推断。 |\n| InfoQuest | search/fetch/image_search。 |\n| Serper | Google Serper search。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Config[config tools provider] --> ToolFactory[get_available_tools]\n  ToolFactory --> Community[community tool module]\n  Community --> Key[read api key or config]\n  Key --> Client[provider client]\n  Client --> External[external search fetch API]\n  External --> Result[normalize text result]\n  Result --> Agent[ToolMessage to agent]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "YI9pdyg9YoDuMCx7sK8mLMn7yHg",
      "revision_id": 18
    }
  }
}
