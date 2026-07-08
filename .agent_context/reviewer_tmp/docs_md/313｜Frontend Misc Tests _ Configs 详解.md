<title>313｜Frontend Misc Tests / Configs 详解</title>

<callout emoji="✅">
**本章目标：**补齐剩余 frontend/UI/misc 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| playwright.record.config.ts | 录制配置。 |
| playwright.real-backend.config.ts | 真实后端 E2E 配置。 |
| vitest.config.ts | 单测配置。 |
| prettier/eslint | 格式和 lint。 |
| components.json | UI 组件配置。 |

```mermaid
flowchart TD
  FrontendSource --> ESLint
  FrontendSource --> Prettier
  FrontendSource --> Vitest
  FrontendSource --> PlaywrightRecord
  FrontendSource --> PlaywrightRealBackend
  ComponentsJson --> UIConfig
  Checks --> CI
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 好处是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 坏处是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```