{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>211｜backend/docs/MCP_SERVER.md 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续把 backend/docs 中重要说明拆成独立讲解文档。\n</callout>\n\n| 文档点 | 说明 |\n|-|-|\n| stdio | npx/uvx 等本地 MCP server。 |\n| SSE/HTTP | 远程 MCP transport。 |\n| OAuth | HTTP/SSE token 注入。 |\n| extensions_config | MCP server 配置存储。 |\n| frontend settings | Tools 设置页管理。 |\n\n```mermaid\nflowchart TD\n  MCPDoc --> Stdio[stdio server]\n  MCPDoc --> HTTP[http sse server]\n  MCPDoc --> OAuth[oauth config]\n  Stdio --> SessionPool\n  HTTP --> MCPClient\n  OAuth --> Headers\n  SessionPool --> Tools\n  MCPClient --> Tools\n  Tools --> Agent\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "CgAadryj6oNzWfxWs3cmY7yPyIb",
      "revision_id": 16
    }
  }
}
