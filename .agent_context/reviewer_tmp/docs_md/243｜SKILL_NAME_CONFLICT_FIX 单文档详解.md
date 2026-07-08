<title>243｜SKILL_NAME_CONFLICT_FIX 单文档详解</title>

<callout emoji="✅">
**本章目标：**继续细化 content/docs/evidence 模块并给出维护逻辑图。
</callout>

| 模块点 | 说明 |
|-|-|
| SKILL_NAME_CONFLICT_FIX.md | skill 命名冲突修复说明。 |
| 关联代码 | skills parser/storage/router。 |
| 风险 | 同名 skill path/category 冲突。 |
| 验证 | skills loader/parser/custom router tests。 |

```mermaid
flowchart TD
  Conflict[skill name conflict] --> Doc[fix doc]
  Doc --> Parser[skills parser]
  Doc --> Storage[skill storage]
  Doc --> Router[skills router]
  Parser --> Tests[skills tests]
  Storage --> Tests
  Router --> Tests
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