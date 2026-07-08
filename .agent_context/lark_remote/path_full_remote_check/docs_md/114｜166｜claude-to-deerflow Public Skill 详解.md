{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>166｜claude-to-deerflow Public Skill 详解</title>\n\n<callout emoji=\"✅\">\n**Skill 目标：**通过 DeerFlow HTTP API 与正在运行的 DeerFlow 实例交互：健康检查、创建 thread、流式 run、列出 models/skills/agents、管理 memory、上传文件和委派研究任务。\n</callout>\n\n| 字段 | 说明 |\n|-|-|\n| Skill 名称 | `claude-to-deerflow` |\n| 路径 | `skills/public/claude-to-deerflow/SKILL.md` |\n| 类型 | DeerFlow HTTP API / LangGraph-compatible runtime client |\n| 触发方式 | 用户提到 DeerFlow、要向 DeerFlow 发消息、检查状态、管理模型/skills/agents/memory、上传文件，或显式 `/claude-to-deerflow` |\n\n```mermaid\nflowchart TD\n  User[User task] --> Resolve[resolve DEERFLOW_URL / GATEWAY / LANGGRAPH env]\n  Resolve --> Health[GET Gateway /health]\n  Resolve --> Thread[POST LangGraph /threads]\n  Thread --> Stream[POST /threads/:id/runs/stream]\n  Stream --> SSE[metadata / values / messages-tuple / end]\n  Resolve --> Ops[models skills agents memory uploads]\n  SSE --> Output[collect final answer or stream events]\n  Ops --> Output\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "TjB5dinPno2umfxVCMxmyN3ByKY",
      "revision_id": 20
    }
  }
}
