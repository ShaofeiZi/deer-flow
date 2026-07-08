{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>137｜Docker Compose、Nginx、Provisioner 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| docker-compose-dev.yaml | Docker 开发环境。 |\n| docker-compose.yaml | 生产容器编排。 |\n| nginx.local.conf/nginx.conf | 统一入口和 /api/langgraph rewrite。 |\n| provisioner/app.py | Kubernetes sandbox provisioner。 |\n| dev-entrypoint.sh | 容器开发入口。 |\n\n## 补充：Docker 与 Nginx 简化运行图\n\n```mermaid\nflowchart TD\n  A[Docker Compose] --> B[Gateway container]\n  A --> C[Frontend container]\n  A --> D[Nginx container]\n  D --> E[api langgraph rewrite]\n  E --> B\n  D --> C\n  B --> F[Sandbox mode]\n  F --> G[Local Docker sandbox]\n  F --> H[Provisioner]\n  H --> I[Kubernetes Pod]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明一个 public skill 或 skill 分类的目标、触发条件、执行链路和维护边界，方便新同学理解 DeerFlow 的可扩展能力。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | skill 能力被文档化后，使用者能快速判断何时触发、读哪些文件、如何验证输出。 |\n| 代价 | skill 文档容易和实际 `SKILL.md` 漂移，需要定期回到源码和示例验证。 |\n| 重点代码 | 对应 `skills/public/.../SKILL.md`、相关 `references/`、`templates/`、`scripts/`。 |\n| 阅读路径 | 先读 skill frontmatter 和触发场景，再读正文 workflow，最后检查 references/templates/scripts 是否支撑描述。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "LHnqdWz1Aoxf7oxQA7nmHDeTy0d",
      "revision_id": 19
    }
  }
}
