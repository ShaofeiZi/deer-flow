<title>344｜Landing CaseStudy / Skills / Sandbox Sections 详解</title>

<callout emoji="✅">
**本章目标：**继续细化前端 UI/Landing/I18n 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| case-study-section.tsx | 案例展示。 |
| skills-section.tsx | skills 能力展示。 |
| sandbox-section.tsx | sandbox 能力展示。 |
| shared section | 共用视觉节奏。 |

```mermaid
flowchart TD
  LandingPage --> CaseStudy
  LandingPage --> SkillsSection
  LandingPage --> SandboxSection
  CaseStudy --> UseCases
  SkillsSection --> SkillCapabilities
  SandboxSection --> IsolationExecution
  UseCases --> UserUnderstanding
  SkillCapabilities --> UserUnderstanding
  IsolationExecution --> UserUnderstanding
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
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```