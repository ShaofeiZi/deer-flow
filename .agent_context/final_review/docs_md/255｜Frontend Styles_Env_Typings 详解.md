<title>255｜Frontend Styles、Env、Typings 详解</title>

<callout emoji="✅">
**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。
</callout>

| 模块点 | 说明 |
|-|-|
| styles/globals.css | 全局样式。 |
| env | Next.js env validation。 |
| typings/md.d.ts | Markdown 类型声明。 |
| tailwind/postcss config | 样式构建。 |
| components.json | shadcn 组件配置。 |

```mermaid
flowchart TD
  CSS[globals css] --> AppLayout
  Env[env validation] --> RuntimeConfig
  Typings[md d ts] --> TSCompiler
  Tailwind[tailwind postcss] --> Build
  ComponentsJson --> UIPrimitives
  Build --> FrontendApp
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
flowchart TD
  Env["env.js createEnv"] --> Config["core/config getLangGraphBaseURL"]
  RootLayout["app/layout RootLayout"] --> I18n["core/i18n/server detectLocaleServer"]
  I18n --> I18nProvider["core/i18n/context I18nProvider"]
  RootLayout --> Theme["components/theme-provider"]
  WSLayout["app/workspace/layout WorkspaceLayout"] --> AuthSrv["core/auth/server getServerSideUser"]
  AuthSrv --> AuthProvider["core/auth/AuthProvider"]
  Config --> ApiClient["core/api/api-client LangGraph SDK"]
  ApiClient --> Fetcher["core/api/fetcher CSRF token"]
  Fetcher --> Gateway["gateway REST endpoints"]
  WSLayout --> WSContent["app/workspace/workspace-content"]
  WSContent --> BizCmp["components/workspace business components"]
  BizCmp --> UIPrim["components/ui primitives"]
  BizCmp --> ApiClient
```