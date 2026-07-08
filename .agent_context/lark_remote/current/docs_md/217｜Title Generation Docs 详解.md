<title>217｜Title Generation Docs 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。
</callout>

| 文档点 | 说明 |
|-|-|
| TITLE_GENERATION_IMPLEMENTATION.md | 标题生成实现说明。 |
| AUTO_TITLE_GENERATION.md | 自动标题功能。 |
| 关联代码 | TitleMiddleware、thread meta。 |
| 测试 | test_title_generation、test_title_middleware_core_logic。 |

```mermaid
flowchart TD
  UserAssistant[First exchange] --> TitleMW[TitleMiddleware]
  TitleMW --> Model[title model or fallback]
  Model --> State[thread state title]
  State --> RunWorker[run worker final sync]
  RunWorker --> ThreadMeta[thread metadata]
  ThreadMeta --> Frontend[sidebar title]
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