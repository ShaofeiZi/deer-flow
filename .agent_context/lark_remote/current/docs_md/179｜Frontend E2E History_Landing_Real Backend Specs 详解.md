<title>179｜Frontend E2E History/Landing/Real Backend Specs 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。
</callout>

| 模块点 | 说明 |
|-|-|
| thread-history.spec.ts | 历史消息。 |
| thread-history-mermaid.spec.ts | Mermaid 历史渲染。 |
| thread-list-infinite-scroll.spec.ts | 会话列表无限滚动。 |
| landing.spec.ts | 首页。 |
| e2e-real-backend | 真实后端契约。 |

```mermaid
flowchart TD
  Playwright --> History[thread history]
  Playwright --> Mermaid[history mermaid]
  Playwright --> Infinite[thread list infinite scroll]
  Playwright --> Landing[landing]
  Playwright --> Real[real backend specs]
  Real --> Gateway[real Gateway]
  History --> MockAPI
  Mermaid --> MockAPI
  Infinite --> MockAPI
  Assertions --> CI
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
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```