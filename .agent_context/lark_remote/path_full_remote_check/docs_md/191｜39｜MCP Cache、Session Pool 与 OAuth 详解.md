{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>39｜MCP Cache、Session Pool 与 OAuth 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 MCP 工具从 extensions_config 加载、缓存、stdio 会话复用和 OAuth token 注入。\n</callout>\n\n| 文件 | 职责 |\n|-|-|\n| `mcp/client.py` | 把 ExtensionsConfig 转成 MultiServerMCPClient server config。 |\n| `mcp/tools.py` | 发现 MCP tools，包装 stdio session pool tool。 |\n| `mcp/cache.py` | 缓存 MCP tools，并按 config mtime 判断 stale。 |\n| `mcp/session_pool.py` | stdio MCP per-thread session 复用和清理。 |\n| `mcp/oauth.py` | HTTP/SSE MCP OAuth token 获取、刷新、header 注入。 |\n\n```mermaid\nflowchart TD\n  Ext[extensions_config.json] --> Client[build_servers_config]\n  Client --> MCPClient[MultiServerMCPClient]\n  MCPClient --> Discover[get_tools]\n  Discover --> Stdio{stdio server?}\n  Stdio -->|yes| Pool[MCPSessionPool wrapper]\n  Stdio -->|no| Direct[direct tool]\n  OAuth[OAuth config] --> Headers[token headers]\n  Headers --> Direct\n  Pool --> Cache[MCP tools cache]\n  Direct --> Cache\n  Cache --> Agent[get_available_tools]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这些模块负责扩展 agent 能力：skill 提供方法论，MCP 提供外部工具，memory 提供长期上下文。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是能力可扩展、可配置、可跨会话复用。 |\n| 代价 | 代价是 prompt、工具、记忆三者都会影响模型行为，问题定位需要分层排查。 |\n| 重点代码 | 重点代码在 `backend/packages/harness/deerflow/skills`、`mcp`、`agents/memory`。 |\n| 阅读路径 | 阅读路径：把 skill 当说明书，MCP 当工具注册表，memory 当上下文注入源。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "RRlAdJ5QeoVOVmxAd5AmHF9Wycf",
      "revision_id": 15
    }
  }
}
