{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>219｜Backend RFC Docs 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。\n</callout>\n\n| 文档点 | 说明 |\n|-|-|\n| rfc-create-deerflow-agent.md | 创建 DeerFlow agent RFC。 |\n| rfc-grep-glob-tools.md | grep/glob tools RFC。 |\n| rfc-extract-shared-modules.md | 共享模块抽取 RFC。 |\n| 关联代码 | agents factory、sandbox search tools、shared modules。 |\n\n```mermaid\nflowchart TD\n  RFC[proposal] --> Design[design decision]\n  Design --> Implementation[code implementation]\n  Implementation --> Tests[tests]\n  RFC1[create agent] --> AgentFactory\n  RFC2[grep glob] --> SandboxSearch\n  RFC3[shared modules] --> Refactor\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "CremdpVhaokfGaxAEj7mzm4ayPN",
      "revision_id": 18
    }
  }
}
