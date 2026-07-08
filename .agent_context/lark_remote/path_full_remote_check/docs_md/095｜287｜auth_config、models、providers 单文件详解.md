{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>287｜auth/config、models、providers 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 auth/channel/frontend core 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| config.py | AuthConfig 和开关。 |\n| models.py | UserResponse 等 API 模型。 |\n| providers.py | 通用 AuthProvider 抽象，定义 authenticate/get_user。 |\n| ../auth_disabled.py | Gateway 级禁用认证模式；文件在 `backend/app/gateway/`，不在 `auth/` 子包内。 |\n| ../langgraph_auth.py | LangGraph compatibility auth handler；复用 Gateway JWT/CSRF 规则。 |\n\n```mermaid\nflowchart TD\n  Config --> AuthConfig\n  AuthConfig --> AuthRouter\n  Models --> APIResponse\n  Providers --> LocalProvider\n  AuthDisabled --> Middleware\n  LangGraphAuth --> LangGraphRoutes\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "FrXYd3OjaoYnKpx1Z3NmqXFEyZd",
      "revision_id": 20
    }
  }
}
