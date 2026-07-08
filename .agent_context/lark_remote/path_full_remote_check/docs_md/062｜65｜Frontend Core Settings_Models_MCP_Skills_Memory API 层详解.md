{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>65｜Frontend Core Settings/Models/MCP/Skills/Memory API 层详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清前端 core data layer 如何和后端 Settings API 对接。\n</callout>\n\n# 1. 模块职责\n\n| 对象 | 说明 |\n|-|-|\n| `frontend/src/core/settings/*` | local settings、thread model override、hooks。 |\n| `frontend/src/core/models/*` | loadModels 与 token usage enabled。 |\n| `frontend/src/core/mcp/*` | load/update MCP config。 |\n| `frontend/src/core/skills/*` | load/enable/install skills。 |\n| `frontend/src/core/memory/*` | memory/facts CRUD、import/export。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  SettingsUI[Settings Pages] --> Hooks[Core hooks]\n  Hooks --> Models[core models api]\n  Hooks --> MCP[core mcp api]\n  Hooks --> Skills[core skills api]\n  Hooks --> Memory[core memory api]\n  Hooks --> Local[core settings localStorage]\n  Models --> API1[GET api models]\n  MCP --> API2[GET PUT api mcp config]\n  Skills --> API3[GET PUT api skills install]\n  Memory --> API4[api memory facts CRUD]\n  Local --> Browser[localStorage]\n```\n\n# 3. 排障与修改建议\n\n- 先确认调用方和数据源，再改 schema。\n- 涉及用户数据必须确认鉴权和 owner check。\n- 涉及缓存需要同步 invalidate 或 reset。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Xfm2d6pOMotWZixrSDcm22bsyic",
      "revision_id": 19
    }
  }
}
