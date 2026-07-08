{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>308｜Workspace Tool/Skill/Memory Settings 页面细节</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐剩余 frontend/UI/misc 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| tool-settings-page.tsx | MCP tools 配置。 |\n| skill-settings-page.tsx | skills 启停与创建。 |\n| memory-settings-page.tsx | memory facts/summaries。 |\n| settings-dialog.tsx | section 切换。 |\n\n```mermaid\nflowchart TD\n  SettingsDialog --> ToolPage\n  SettingsDialog --> SkillPage\n  SettingsDialog --> MemoryPage\n  ToolPage --> MCPHooks\n  SkillPage --> SkillsHooks\n  MemoryPage --> MemoryHooks\n  MCPHooks --> GatewayMCP\n  SkillsHooks --> GatewaySkills\n  MemoryHooks --> GatewayMemory\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**Tool/Skill/Memory Settings 页面把可扩展能力的后端管理 API 接入到 Settings 弹窗，并通过 React Query 管理加载、错误和缓存失效。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | MCP、Skills、Memory 的列表、启停、CRUD、导入导出都有统一 UI 入口。 |\n| 代价 | 每页都跨前端 hook、Gateway API、缓存失效和静态站点禁用分支。 |\n| 重点代码 | `frontend/src/components/workspace/settings/tool-settings-page.tsx`、`frontend/src/components/workspace/settings/skill-settings-page.tsx`、`frontend/src/components/workspace/settings/memory-settings-page.tsx`、`frontend/src/core/mcp/`、`frontend/src/core/skills/`、`frontend/src/core/memory/`。 |\n| 阅读路径 | 先看页面如何调用 hook，再看 hook 如何调用 API 和更新 React Query cache。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```\n\n## Settings 数据流补充\n\n| 页面 | 数据源 | 写入/副作用 |\n|-|-|-|\n| Tools | `useMCPConfig()` -> `loadMCPConfig()` | `useEnableMCPServer()` 更新 config，成功后 invalidate `mcpConfig`；静态站点禁用 switch。 |\n| Skills | `useSkills()` -> `loadSkills()` | `useEnableSkill()` 后 invalidate `skills`；Create Skill 关闭弹窗并跳转 `/workspace/chats/new?mode=skill`。 |\n| Memory | `useMemory()` -> `loadMemory()` | clear/delete/import/create/update 直接更新 React Query `memory` cache；export 走 `exportMemory()`。 |",
      "document_id": "A1SjdgFxKoBrcMxPbMLmMQ0iyGf",
      "revision_id": 20
    }
  }
}
