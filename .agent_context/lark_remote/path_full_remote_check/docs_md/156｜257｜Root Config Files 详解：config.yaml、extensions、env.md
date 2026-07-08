{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 257｜Root Config Files 详解：config.yaml、extensions、env\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| config.example.yaml | 主配置模板。 |\n| config.yaml | 本地真实配置。 |\n| extensions_config.example.json | MCP/skills 状态模板。 |\n| extensions_config.json | 本地扩展配置。 |\n| .env/.env.example | 环境变量和 API key。 |\n\n```mermaid\nflowchart TD\n  EnvFile[env files] --> AppConfig\n  ConfigExample --> ConfigYaml\n  ConfigYaml --> AppConfig\n  ExtensionsExample --> ExtensionsConfig\n  ExtensionsConfig --> MCPServers\n  ExtensionsConfig --> SkillState\n  AppConfig --> Runtime\n  MCPServers --> AgentTools\n  SkillState --> SkillPrompt\n```",
      "document_id": "MTLodmuoco6IVnxjtdEm1suxyZe",
      "revision_id": 18
    }
  }
}
