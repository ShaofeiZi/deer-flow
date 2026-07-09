<title>134｜GitHub Workflows CI 流水线详解</title>

<callout emoji="✅">
**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| backend-unit-tests.yml | 后端 pytest。 |
| frontend-unit-tests.yml | 前端单测/类型。 |
| e2e-tests.yml | Playwright E2E。 |
| replay-e2e.yml | Replay 契约。 |
| backend-blocking-io-tests.yml | 阻塞 IO gate。 |
| lint-check.yml | lint 检查。 |
| container.yaml | 容器构建。 |

```mermaid
flowchart TD
  Push[push or PR] --> Backend[backend unit tests]
  Push --> Frontend[frontend unit tests]
  Push --> E2E[e2e tests]
  Push --> Replay[replay e2e]
  Push --> Blocking[blocking io tests]
  Push --> Lint[lint check]
  Push --> Container[container build]
  Results --> PRStatus[PR checks]
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