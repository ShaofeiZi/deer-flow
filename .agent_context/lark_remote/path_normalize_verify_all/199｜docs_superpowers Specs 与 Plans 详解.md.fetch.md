{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>199｜docs/superpowers Specs 与 Plans 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续补齐剩余测试与文档规格模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| docs/superpowers/specs | 功能设计规格。 |\n| docs/superpowers/plans | 实施计划。 |\n| docs/plans | 历史/局部计划。 |\n| docs/pr-evidence | PR 证据截图。 |\n| CODE_CHANGE_SUMMARY | 文件级变更摘要。 |\n\n```mermaid\nflowchart TD\n  Idea[feature idea] --> Spec[docs superpowers specs]\n  Spec --> Plan[docs superpowers plans]\n  Plan --> Implementation[code changes]\n  Implementation --> Evidence[docs pr evidence]\n  Evidence --> Review[review and merge]\n  ChangeSummary --> Review\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "OjF7dbZv9oB1mAxCzmim9i50yxJ",
      "revision_id": 18
    }
  }
}
