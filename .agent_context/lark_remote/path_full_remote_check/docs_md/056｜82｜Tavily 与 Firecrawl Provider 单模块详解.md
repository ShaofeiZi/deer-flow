{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>82｜Tavily 与 Firecrawl Provider 单模块详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**细化两个常用 web_search/web_fetch provider 的运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Tavily | `_get_tavily_client` 读取 key，web_search/web_fetch 返回文本结果。 |\n| Firecrawl | `FirecrawlApp` 创建 client，search/fetch 页面内容。 |\n| 共同点 | 都是 community tool module，最终作为 BaseTool 进入 agent。 |\n| 差异 | Firecrawl 更偏网页抓取，Tavily 更偏搜索 API。 |\n\n```mermaid\nflowchart TD\n  Agent[agent calls web_search or web_fetch] --> Select[configured provider]\n  Select --> Tavily[Tavily tools]\n  Select --> Firecrawl[Firecrawl tools]\n  Tavily --> TKey[TAVILY API key]\n  Firecrawl --> FKey[Firecrawl key]\n  TKey --> TClient[TavilyClient]\n  FKey --> FClient[FirecrawlApp]\n  TClient --> Result[normalized text]\n  FClient --> Result\n  Result --> Agent\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "BJQTdmcNBow7eMxwAIEm0yjPyxh",
      "revision_id": 18
    }
  }
}
