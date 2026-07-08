{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 273｜skill_manage_tool / sync / mcp_metadata / types 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 tools/reflection/utils 等基础模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| skill_manage_tool.py | agent 创建/编辑 custom skill。 |\n| sync.py | 同步类工具辅助。 |\n| mcp_metadata.py | MCP metadata 辅助。 |\n| types.py | 工具 runtime/type 定义。 |\n| \\_\\_init\\_\\_.py | tools 包导出。 |\n\n```mermaid\nflowchart TD\n  Agent --> SkillManageTool\n  SkillManageTool --> CustomSkills\n  Tools --> RuntimeTypes\n  MCPTools --> MCPMetadata\n  SyncNeed --> SyncHelpers\n  PackageInit --> GetAvailableTools\n  CustomSkills --> SkillStorage\n```",
      "document_id": "T1mhdUid6oqejwxLQxpmTbclySf",
      "revision_id": 18
    }
  }
}
