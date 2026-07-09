<title>198｜Frontend Unit 与 Real Backend Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续补齐剩余测试与文档规格模块。
</callout>

| 模块点 | 说明 |
|-|-|
| unit/core/clipboard.test.ts | 剪贴板单测。 |
| unit/core/reasoning-trigger.test.ts | reasoning 触发单测。 |
| e2e-real-backend/auth-disabled-contract | 真实后端 auth disabled 合同。 |
| e2e-real-backend/multi-run-order | 多 run 顺序。 |
| e2e-real-backend/real-backend-render | 真实后端渲染。 |

```mermaid
flowchart TD
  FrontendCore --> UnitTests
  UnitTests --> Clipboard
  UnitTests --> ReasoningTrigger
  RealBackend --> AuthContract
  RealBackend --> MultiRunOrder
  RealBackend --> Render
  AuthContract --> Gateway
  MultiRunOrder --> Gateway
  Render --> BrowserAssertions
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
sequenceDiagram
    participant spec as multi-run-order.spec
    participant page as Playwright page
    participant next as next.config rewrite
    participant gw as replay gateway
    participant hist as useThreadHistory
    participant runs as useThreadRuns
    participant merge as mergeMessages

    spec->>next: POST /api/v1/auth/register
    next->>gw: same-origin proxy to /api/v1/auth/register
    gw-->>spec: 201 plus csrf_token cookie
    spec->>next: POST /api/test-only/seed-runs
    next->>gw: seed ALPHA older and OMEGA newer
    spec->>page: goto /workspace/chats/threadId
    page->>hist: mount thread view
    hist->>runs: list runs by thread
    runs->>gw: runs.list newest-first
    runs-->>hist: run list ALPHA then OMEGA
    hist->>gw: GET run messages buildRunMessagesUrl
    gw-->>hist: per-run message pages
    hist->>merge: prepend loaded pages
    merge-->>page: chronological message list
    page-->>spec: ALPHA rendered above OMEGA
    spec->>spec: assert ALPHA y less than OMEGA y
```