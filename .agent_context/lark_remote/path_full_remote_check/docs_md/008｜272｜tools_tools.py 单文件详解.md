{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>272｜tools/tools.py 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 tools/reflection/utils 等基础模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| get_available_tools | 聚合内置、sandbox、community、MCP 工具。 |\n| groups | 按工具组过滤。 |\n| subagent_enabled | 决定是否加入 task tool。 |\n| app_config | 从 AppConfig 读取工具配置。 |\n\n```mermaid\nflowchart TD\n  AppConfig --> GetTools[get_available_tools]\n  GetTools --> Builtins\n  GetTools --> SandboxTools\n  GetTools --> CommunityTools\n  GetTools --> MCPTools\n  SubagentEnabled --> TaskTool\n  TaskTool --> GetTools\n  Groups --> Filter\n  Filter --> FinalTools[tools for agent]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |\n| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |\n| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |\n| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "T1jXda6EUoTqlGxFCbImuL8uy4P",
      "revision_id": 18
    }
  }
}
