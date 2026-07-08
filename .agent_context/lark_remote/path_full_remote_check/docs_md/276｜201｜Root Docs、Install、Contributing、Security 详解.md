{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>201｜Root Docs、Install、Contributing、Security 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续补齐剩余测试与文档规格模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| README_zh/README | 项目定位与快速开始。 |\n| Install.md | 给 coding agent 的安装初始化说明。 |\n| CONTRIBUTING.md | 贡献流程。 |\n| SECURITY.md | 安全说明。 |\n| CODE_OF_CONDUCT.md | 社区规范。 |\n\n```mermaid\nflowchart TD\n  User --> README[README]\n  README --> Install[Install md]\n  Contributor --> Contributing[CONTRIBUTING]\n  SecurityIssue --> Security[SECURITY]\n  Community --> CodeOfConduct[CODE OF CONDUCT]\n  Install --> Setup[make config install dev]\n  Contributing --> PR[Pull Request]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切逻辑从核心 agent 流程里剥离，按 before/after/wrap 阶段插入。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是职责独立、便于单测和按配置启停。 |\n| 代价 | 代价是顺序和状态合并不直观，多 middleware 同时改 messages/state 时需要按链路排查。 |\n| 重点代码 | 重点代码在 `backend/packages/harness/deerflow/agents/middlewares/` 对应文件，优先看 hook 方法。 |\n| 阅读路径 | 阅读路径：先定位 hook 阶段，再看它读写哪个 state 字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "JcildSxKLoDd3vxnDBtmT1HkyJe",
      "revision_id": 16
    }
  }
}
