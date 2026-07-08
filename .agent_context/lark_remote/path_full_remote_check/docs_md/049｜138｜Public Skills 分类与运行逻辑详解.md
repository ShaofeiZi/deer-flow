{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>138｜Public Skills 分类与运行逻辑详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Research | deep-research、github-deep-research、academic-paper-review、systematic-literature-review。 |\n| Generation | image/music/video/podcast/ppt/newsletter。 |\n| Development | frontend-design、code-documentation、vercel-deploy、claude-to-deerflow。 |\n| Analysis | data-analysis、consulting-analysis、chart-visualization。 |\n| Meta | skill-creator、find-skills、bootstrap、surprise-me。 |\n\n## 补充：Public Skills 分类简化运行图\n\n```mermaid\nflowchart TD\n  A[skills public] --> B[Skill parser]\n  B --> C[Research skills]\n  B --> D[Generation skills]\n  B --> E[Development skills]\n  B --> F[Analysis skills]\n  B --> G[Meta skills]\n  H[enabled state] --> I[Prompt metadata]\n  J[user slash skill] --> K[SkillActivationMiddleware]\n  K --> L[Read full SKILL md]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明一个 public skill 或 skill 分类的目标、触发条件、执行链路和维护边界，方便新同学理解 DeerFlow 的可扩展能力。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | skill 能力被文档化后，使用者能快速判断何时触发、读哪些文件、如何验证输出。 |\n| 代价 | skill 文档容易和实际 `SKILL.md` 漂移，需要定期回到源码和示例验证。 |\n| 重点代码 | 对应 `skills/public/.../SKILL.md`、相关 `references/`、`templates/`、`scripts/`。 |\n| 阅读路径 | 先读 skill frontmatter 和触发场景，再读正文 workflow，最后检查 references/templates/scripts 是否支撑描述。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "R7Tddja3zoy1lpxB3aVmnNrUyCe",
      "revision_id": 19
    }
  }
}
