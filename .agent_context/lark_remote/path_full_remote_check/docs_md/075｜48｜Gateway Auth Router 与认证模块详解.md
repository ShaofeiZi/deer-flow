{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>48｜Gateway Auth Router 与认证模块详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**把 auth.py、AuthMiddleware、CSRF、本地用户 provider 的协作讲清。\n</callout>\n\n| 模块 | 职责 |\n|-|-|\n| `routers/auth.py` | 登录、注册、退出、修改密码、初始化 admin、OAuth callback。 |\n| `auth_middleware.py` | 请求级认证，把 user 写入 request.state。 |\n| `csrf_middleware.py` | 状态变更请求 CSRF 校验。 |\n| `auth/local_provider.py` | 本地用户认证 provider。 |\n| `auth/password.py` | 密码 hash 和校验。 |\n\n```mermaid\nsequenceDiagram\n  participant UI as Login UI\n  participant Auth as auth router\n  participant Provider as LocalAuthProvider\n  participant Cookie as HttpOnly Cookie\n  participant MW as AuthMiddleware\n  UI->>Auth: POST login local\n  Auth->>Provider: verify password\n  Provider-->>Auth: UserRow\n  Auth->>Cookie: set session cookie and csrf cookie\n  UI->>MW: later API request\n  MW->>Cookie: read session\n  MW->>Provider: load user\n  MW-->>UI: request.state.user available\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "RIpxddfV7oVl1pxsy2wmbgxty5f",
      "revision_id": 17
    }
  }
}
