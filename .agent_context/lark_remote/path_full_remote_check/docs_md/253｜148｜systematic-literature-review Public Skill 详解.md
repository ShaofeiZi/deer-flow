{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>148｜systematic-literature-review Public Skill 详解</title>\n\n<callout emoji=\"✅\">\n**Skill 目标：**系统文献综述流程。\n</callout>\n\n| 字段 | 说明 |\n|-|-|\n| Skill 名称 | `systematic-literature-review` |\n| 路径 | `skills/public/systematic-literature-review/SKILL.md` |\n| 类型 | literature review |\n| 触发方式 | 任务匹配或显式 `/systematic-literature-review` |\n\n```mermaid\nflowchart TD\n  User[User task] --> Match[match systematic-literature-review]\n  Match --> Read[read skills public systematic-literature-review SKILL md]\n  Read --> Workflow[literature review workflow]\n  Workflow --> Tools[use scripts/tools if needed]\n  Tools --> Output[deliver result]\n  Output --> Memory[agent may continue or summarize]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "VHwydVr3Po77tlxLDy6mLagjy7g",
      "revision_id": 16
    }
  }
}
