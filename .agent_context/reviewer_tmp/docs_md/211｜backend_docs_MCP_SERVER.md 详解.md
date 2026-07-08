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
| 收益 | 好处是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 坏处是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```