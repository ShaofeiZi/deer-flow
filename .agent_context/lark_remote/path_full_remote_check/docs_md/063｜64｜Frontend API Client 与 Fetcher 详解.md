{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>64｜Frontend API Client 与 Fetcher 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 LangGraph SDK client、CSRF 注入、普通 REST fetcher 和 stream mode 清洗。\n</callout>\n\n# 1. 模块职责\n\n| 对象 | 说明 |\n|-|-|\n| `api-client.ts` | 创建 LangGraphClient，包装 runs.stream/joinStream。 |\n| `fetcher.ts` | 普通 REST fetch，自动带 credentials/CSRF。 |\n| `stream-mode.ts` | 过滤不支持的 stream modes。 |\n| `config/index.ts` | 解析 Backend/LangGraph base URL。 |\n| `static-mode` | 静态站点 mock client fallback。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  UI[Frontend Hook] --> Client[getAPIClient]\n  Client --> Base[getLangGraphBaseURL]\n  Client --> CSRF[inject X CSRF Token]\n  Client --> SDK[LangGraphClient]\n  SDK --> Stream[run stream]\n  Stream --> Sanitize[sanitize stream modes]\n  Rest[REST hooks] --> Fetcher[fetchWithAuth]\n  Fetcher --> CSRF2[get csrf headers]\n  Fetcher --> Gateway[Gateway API]\n```\n\n# 3. 排障与修改建议\n\n- 先确认调用方和数据源，再改 schema。\n- 涉及用户数据必须确认鉴权和 owner check。\n- 涉及缓存需要同步 invalidate 或 reset。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Vdnzdq4HfoAl4pxJk1VmQnpAyGg",
      "revision_id": 17
    }
  }
}
