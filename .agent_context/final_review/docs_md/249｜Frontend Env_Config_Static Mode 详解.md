<title>249｜Frontend Env、Config、Static Mode 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试 helper、fixtures、frontend content 支持模块。
</callout>

| 模块点 | 说明 |
|-|-|
| env | Next.js 环境变量。 |
| core/config/index.ts | 后端/LangGraph base URL。 |
| core/static-mode.ts | 静态站点模式判断。 |
| threads/static-demo.ts | 静态 demo threads。 |
| api-client static client | mock LangGraph client。 |

```mermaid
flowchart TD
  EnvVars --> CoreConfig
  CoreConfig --> BackendURL
  CoreConfig --> LangGraphURL
  StaticFlag --> StaticMode
  StaticMode --> StaticClient
  StaticClient --> DemoThreads
  DemoThreads --> UI
  BackendURL --> Fetcher
  LangGraphURL --> APIClient
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
  Env["env.js createEnv"] --> Flag["NEXT_PUBLIC_STATIC_WEBSITE_ONLY"]
  Env --> Backend["NEXT_PUBLIC_BACKEND_BASE_URL"]
  Env --> LangURL["NEXT_PUBLIC_LANGGRAPH_BASE_URL"]
  Flag --> Static["isStaticWebsiteOnly"]
  Backend --> CfgBackend["getBackendBaseURL"]
  LangURL --> CfgLang["getLangGraphBaseURL"]
  GetAPI["getAPIClient"] --> Create["createCompatibleClient"]
  Static --> Create
  Create -->|"static and not mock"| StaticClient["createStaticClient"]
  Create -->|"real or mock"| RealClient["LangGraphClient + injectCsrfHeader"]
  CfgLang --> RealClient
  StaticClient --> DemoSearch["threads.search to loadStaticDemoThreads"]
  StaticClient --> DemoGet["threads.get to loadStaticDemoThread"]
  DemoSearch --> FetchDemo["fetch /demo/threads/thread.json"]
  DemoGet --> FetchDemo
  FetchDemo --> ThreadState["staticDemoThreadState"]
```