<title>235｜Summarize Marker Spec 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续细化 content/spec/docs 单模块，补充运行/维护逻辑图。
</callout>

| 模块点 | 说明 |
|-|-|
| spec | 2026-04-11-summarize-marker-design.md。 |
| 目标 | 摘要边界可追踪。 |
| 关联 | SummarizationMiddleware。 |
| 验证 | 长对话摘要测试。 |

```mermaid
flowchart TD
  LongConversation --> SummaryTrigger
  SummaryTrigger --> Marker[summary marker]
  Marker --> SummarizationMiddleware
  SummarizationMiddleware --> NewMessages
  NewMessages --> History
  Tests --> MarkerBehavior
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