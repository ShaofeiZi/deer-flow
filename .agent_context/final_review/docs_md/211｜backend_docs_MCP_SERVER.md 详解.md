<title>211｜backend/docs/MCP_SERVER.md 详解</title>

<callout emoji="✅">
**本章目标：**继续把 backend/docs 中重要说明拆成独立讲解文档。
</callout>

| 文档点 | 说明 |
|-|-|
| stdio | npx/uvx 等本地 MCP server。 |
| SSE/HTTP | 远程 MCP transport。 |
| OAuth | HTTP/SSE token 注入。 |
| extensions_config | MCP server 配置存储。 |
| frontend settings | Tools 设置页管理。 |

```mermaid
flowchart TD
  MCPDoc --> Stdio[stdio server]
  MCPDoc --> HTTP[http sse server]
  MCPDoc --> OAuth[oauth config]
  Stdio --> SessionPool
  HTTP --> MCPClient
  OAuth --> Headers
  SessionPool --> Tools
  MCPClient --> Tools
  Tools --> Agent
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
sequenceDiagram
  participant FE as frontend hooks
  participant Router as mcp.py PUT /api/mcp/config
  participant Cfg as extensions_config.json
  participant Cache as cache.py
  participant Tools as tools.py get_mcp_tools
  participant OAuth as OAuthTokenManager
  participant Client as MultiServerMCPClient
  participant Pool as MCPSessionPool

  FE->>Router: PUT mcp_servers masked
  Router->>Router: _validate_mcp_update_request stdio allowlist
  Router->>Cfg: _merge_preserving_secrets write
  Router->>Cfg: reload_extensions_config
  Note over Cache: next get_cached_mcp_tools sees stale mtime
  Cache->>Cache: _is_cache_stale reset_mcp_tools_cache
  Cache->>Pool: close_all_sync
  Cache->>Tools: initialize_mcp_tools
  Tools->>Cfg: ExtensionsConfig.from_file
  Tools->>Tools: build_servers_config per server
  Tools->>OAuth: get_initial_oauth_headers
  OAuth-->>Tools: Authorization headers sse http
  Tools->>Client: get_tools discover
  Client-->>Tools: BaseTool list
  Tools->>Tools: wrap stdio tools _make_session_pool_tool
  Tools->>Tools: make_sync_tool_wrapper
  Tools-->>Cache: wrapped tools cached
```