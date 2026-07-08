{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>173｜Setup Wizard Scripts 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/CI/脚本模块，说明覆盖范围、运行入口和逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| setup_wizard.py | 交互式初始化总入口。 |\n| wizard/ui.py | 交互 UI。 |\n| wizard/providers.py | provider 配置逻辑。 |\n| steps/llm.py | 模型/API key 配置。 |\n| steps/search.py | 搜索工具配置。 |\n| steps/execution.py | 执行/sandbox 相关配置。 |\n| wizard/writer.py | 写入 config。 |\n\n```mermaid\nflowchart TD\n  User --> SetupWizard[setup_wizard]\n  SetupWizard --> UI[wizard ui]\n  UI --> Providers[providers]\n  UI --> LLM[steps llm]\n  UI --> Search[steps search]\n  UI --> Execution[steps execution]\n  LLM --> Writer[writer]\n  Search --> Writer\n  Execution --> Writer\n  Writer --> Config[config yaml]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "IvFddjdM4oFm6nxy72mmK3oky5g",
      "revision_id": 16
    }
  }
}
