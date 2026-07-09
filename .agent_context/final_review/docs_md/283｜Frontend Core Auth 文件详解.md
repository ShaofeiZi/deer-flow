<title>283｜Frontend Core Auth 文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 channels/auth/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| AuthProvider.tsx | 客户端认证上下文。 |
| server.ts | 服务端获取 user。 |
| types.ts | auth 类型。 |
| gateway-config.ts | gateway auth 配置读取。 |
| proxy-policy.ts | 代理策略。 |
| static-user/auth-disabled-user | 静态/禁用 auth 用户。 |

```mermaid
flowchart TD
  Layout --> ServerUser[getServerSideUser]
  ServerUser --> AuthProvider
  AuthProvider --> useAuth
  GatewayConfig --> ServerUser
  ProxyPolicy --> ServerUser
  StaticMode --> StaticUser
  AuthDisabled --> AuthDisabledUser
  useAuth --> UI
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
stateDiagram-v2
  [*] --> CheckMode
  CheckMode --> StaticUser: isStaticWebsiteOnly
  CheckMode --> DisabledUser: isAuthDisabledMode
  CheckMode --> ReadCookie: otherwise
  ReadCookie --> ConfigError: getGatewayConfig throws
  ReadCookie --> NoCookie: no access_token
  ReadCookie --> FetchMe: cookie present
  NoCookie --> SystemSetupRequired: setup-status needs_setup
  NoCookie --> Unauthenticated: setup-status ok or unreachable
  FetchMe --> Authenticated: /api/v1/auth/me 200 and userSchema ok
  FetchMe --> NeedsSetup: parsed needs_setup true
  FetchMe --> Unauthenticated: 401 or 403
  FetchMe --> GatewayUnavailable: malformed or non-200 or timeout
  Authenticated --> AuthProvider: initialUser
  NeedsSetup --> SetupRedirect: layout redirect /setup
  SystemSetupRequired --> SetupRedirect: layout redirect /setup
  Unauthenticated --> LoginRedirect: layout redirect /login
  GatewayUnavailable --> OfflineFallback: GatewayOfflineFallback
  ConfigError --> [*]: layout throws
  StaticUser --> AuthProvider
  DisabledUser --> AuthProvider
```