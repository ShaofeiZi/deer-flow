{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>140｜Media Generation Public Skills 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**把 public skills 按能力组拆开，说明触发场景、工作流和运行逻辑。\n</callout>\n\n| Skill | 职责 |\n|-|-|\n| `image-generation` | 图片生成。 |\n| `music-generation` | 音乐生成。 |\n| `video-generation` | 视频生成。 |\n| `podcast-generation` | 播客生成。 |\n| `ppt-generation` | PPT 生成。 |\n| `newsletter-generation` | newsletter 生成。 |\n\n```mermaid\nflowchart TD\n  User[User task] --> Match[Skill relevance or slash command]\n  Match --> Load[read SKILL md]\n  Load --> Plan[media generation workflow]\n  Plan --> Tools[use allowed tools or scripts]\n  Tools --> Output[deliver artifact or answer]\n  Output --> Agent[agent continues conversation]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明一个 public skill 或 skill 分类的目标、触发条件、执行链路和维护边界，方便新同学理解 DeerFlow 的可扩展能力。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | skill 能力被文档化后，使用者能快速判断何时触发、读哪些文件、如何验证输出。 |\n| 代价 | skill 文档容易和实际 `SKILL.md` 漂移，需要定期回到源码和示例验证。 |\n| 重点代码 | 对应 `skills/public/.../SKILL.md`、相关 `references/`、`templates/`、`scripts/`。 |\n| 阅读路径 | 先读 skill frontmatter 和触发场景，再读正文 workflow，最后检查 references/templates/scripts 是否支撑描述。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "JB1TdkfzAo4Cxzx65lDmUwPnytc",
      "revision_id": 18
    }
  }
}
