{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>170｜Backend Sandbox/MCP/Memory Tests 分类详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/CI/脚本模块，说明覆盖范围、运行入口和逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| sandbox tests | local/aio sandbox、路径、安全、搜索。 |\n| MCP tests | client config、OAuth、session pool、secrets。 |\n| memory tests | storage、queue、router、updater、user isolation。 |\n| community tools tests | ddg/exa/firecrawl/infoquest/jina/serper。 |\n\n```mermaid\nflowchart TD\n  Sandbox --> SandboxTests\n  MCP --> MCPTests\n  Memory --> MemoryTests\n  Community --> CommunityTests\n  SandboxTests --> Security[path and bash security]\n  MCPTests --> Config[config and session]\n  MemoryTests --> Isolation[user isolation]\n  CommunityTests --> Provider[provider behavior]\n  Security --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这组测试保护 agent 执行环境的边界能力：sandbox 路径与 bash 安全、MCP 配置/OAuth/session/secrets、memory 的 storage/queue/router/updater 与 user isolation，以及 community provider 行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 外部工具、长期记忆、沙箱文件系统和第三方 provider 的高风险边界都有可回归证据。 |\n| 代价 | 问题常跨配置、运行时 ContextVar、文件路径、后台队列和 provider wrapper。 |\n| 重点代码 | `backend/packages/harness/deerflow/sandbox/`、`backend/packages/harness/deerflow/agents/memory/`、`backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py`、`backend/app/gateway/routers/memory.py`、`backend/packages/harness/deerflow/mcp/` 与 community provider 模块。 |\n| 阅读路径 | 先按测试名定位 sandbox/MCP/memory/provider 子系统，再确认配置入口、用户上下文、持久化路径和失败降级分支。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "GkTPdXagboZghKxHpjDm0EwaySb",
      "revision_id": 18
    }
  }
}
