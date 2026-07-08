{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>184｜Skills / Tools / Deferred Tests 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| test_skills\\_\\* | skills parser/installer/loader/custom router。 |\n| test_skill_manage_tool.py | skill_manage_tool。 |\n| test_tool_search.py | tool search。 |\n| test_deferred\\_\\* | deferred tools promotion/filter。 |\n| test_tool_output\\_\\* | 工具输出截断/预算。 |\n\n```mermaid\nflowchart TD\n  UserMsg[visible user message: /skill-name task] --> Parse[parse_slash_skill_reference]\n  Parse --> Resolve[resolve installed enabled available skill]\n  Resolve --> Read[read SKILL.md under skills root]\n  Read --> Hidden[insert hidden HumanMessage activation context]\n  Hidden --> ModelCall[model call sees skill content + original user message]\n  Hidden --> Audit[RunJournal middleware audit: skill_activation]\n  UserMsg --> Preserve[original user content remains in state/UI]\n  Deferred --> DeferredTests[promotion/filter/cross-context tests]\n  ToolOutput --> OutputTests[truncate/externalize/budget tests]\n  ModelCall --> CI[backend unit tests]\n  DeferredTests --> CI\n  OutputTests --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |\n| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |\n| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |\n| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "EpjFd94nOou7CyxzNjImWfMiylm",
      "revision_id": 20
    }
  }
}
