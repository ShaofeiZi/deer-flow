{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>271｜Built-in Tools：view_image/tool_search/invoke_acp 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| view_image_tool.py | 读取图片给视觉模型。 |\n| tool_search.py | deferred tool catalog/search/promote。 |\n| invoke_acp_agent_tool.py | 调用外部 ACP agent。 |\n| skill_manage_tool.py | agent 管理 custom skills。 |\n\n```mermaid\nflowchart TD\n  UserNeed --> ToolSearch\n  ToolSearch --> Catalog[deferred catalog]\n  Catalog --> Promote[promote tools]\n  ImagePath --> ViewImage\n  ViewImage --> ViewedImagesState\n  ACPRequest --> InvokeACP\n  InvokeACP --> ExternalAgent\n  SkillRequest --> SkillManageTool\n  SkillManageTool --> SkillsCustom\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |\n| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |\n| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |\n| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "ZEm5dEe2QouWJcxhxYsmyXYOyAg",
      "revision_id": 18
    }
  }
}
