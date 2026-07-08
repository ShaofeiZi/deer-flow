<title>199｜docs/superpowers Specs 与 Plans 详解</title>

<callout emoji="✅">
**本章目标：**继续补齐剩余测试与文档规格模块。
</callout>

| 模块点 | 说明 |
|-|-|
| docs/superpowers/specs | 功能设计规格。 |
| docs/superpowers/plans | 实施计划。 |
| docs/plans | 历史/局部计划。 |
| docs/pr-evidence | PR 证据截图。 |
| CODE_CHANGE_SUMMARY | 文件级变更摘要。 |

```mermaid
flowchart TD
  Idea[feature idea] --> Spec[docs superpowers specs]
  Spec --> Plan[docs superpowers plans]
  Plan --> Implementation[code changes]
  Implementation --> Evidence[docs pr evidence]
  Evidence --> Review[review and merge]
  ChangeSummary --> Review
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 好处是前后端契约清晰，接口可独立演进。 |
| 代价 | 坏处是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```