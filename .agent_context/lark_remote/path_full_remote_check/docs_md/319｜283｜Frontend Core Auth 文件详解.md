{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>283｜Frontend Core Auth 文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 channels/auth/frontend core 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| AuthProvider.tsx | 客户端认证上下文。 |\n| server.ts | 服务端获取 user。 |\n| types.ts | auth 类型。 |\n| gateway-config.ts | gateway auth 配置读取。 |\n| proxy-policy.ts | 代理策略。 |\n| static-user/auth-disabled-user | 静态/禁用 auth 用户。 |\n\n```mermaid\nflowchart TD\n  Layout --> ServerUser[getServerSideUser]\n  ServerUser --> AuthProvider\n  AuthProvider --> useAuth\n  GatewayConfig --> ServerUser\n  ProxyPolicy --> ServerUser\n  StaticMode --> StaticUser\n  AuthDisabled --> AuthDisabledUser\n  useAuth --> UI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "ZdKudf7Z8oBjApxZthUm8RRHyZc",
      "revision_id": 16
    }
  }
}
