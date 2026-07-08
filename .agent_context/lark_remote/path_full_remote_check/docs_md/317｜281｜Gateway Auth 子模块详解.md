{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>281｜Gateway Auth 子模块详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 channels/auth/frontend core 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| auth/config.py | auth 配置。 |\n| auth/models.py | UserResponse 等模型。 |\n| auth/jwt.py | JWT/session token。 |\n| auth/password.py | 密码 hash。 |\n| auth/errors.py | 错误码。 |\n| auth/providers.py | OAuth provider 抽象。 |\n\n```mermaid\nflowchart TD\n  AuthRouter --> AuthConfig\n  AuthRouter --> UserModels\n  AuthRouter --> JWT\n  AuthRouter --> Password\n  AuthRouter --> Errors\n  OAuth --> Providers\n  Password --> LocalProvider\n  JWT --> Cookie\n  Errors --> APIResponse\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "HMYDdvXZuoeJxNx8f64mClbVyUh",
      "revision_id": 18
    }
  }
}
