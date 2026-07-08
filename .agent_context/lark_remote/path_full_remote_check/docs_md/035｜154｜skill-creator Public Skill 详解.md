{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>154｜skill-creator Public Skill 详解</title>\n\n<callout emoji=\"✅\">\n**Skill 目标：**创建新 skill 的结构化流程。\n</callout>\n\n| 字段 | 说明 |\n|-|-|\n| Skill 名称 | `skill-creator` |\n| 路径 | `skills/public/skill-creator/SKILL.md` |\n| 类型 | skill authoring |\n| 触发方式 | 任务匹配或显式 `/skill-creator` |\n\n```mermaid\nflowchart TD\n  User[User task] --> Match[match skill-creator]\n  Match --> Read[read skills public skill-creator SKILL md]\n  Read --> Workflow[skill authoring workflow]\n  Workflow --> Tools[use scripts/tools if needed]\n  Tools --> Output[deliver result]\n  Output --> Memory[agent may continue or summarize]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明一个 public skill 或 skill 分类的目标、触发条件、执行链路和维护边界，方便新同学理解 DeerFlow 的可扩展能力。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | skill 能力被文档化后，使用者能快速判断何时触发、读哪些文件、如何验证输出。 |\n| 代价 | skill 文档容易和实际 `SKILL.md` 漂移，需要定期回到源码和示例验证。 |\n| 重点代码 | 对应 `skills/public/.../SKILL.md`、相关 `references/`、`templates/`、`scripts/`。 |\n| 阅读路径 | 先读 skill frontmatter 和触发场景，再读正文 workflow，最后检查 references/templates/scripts 是否支撑描述。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "V32AdbOFKozFkfxolgUmvIeTyzf",
      "revision_id": 18
    }
  }
}
