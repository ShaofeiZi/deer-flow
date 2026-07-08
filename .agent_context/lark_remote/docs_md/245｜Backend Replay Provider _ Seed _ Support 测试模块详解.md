<title>245｜Backend Replay Provider / Seed / Support 测试模块详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试 helper、fixtures、frontend content 支持模块。
</callout>

| 模块点 | 说明 |
|-|-|
| replay_provider.py | replay provider 测试支持。 |
| seed_runs_router.py | run router seed 数据。 |
| support/\_\_init\_\_.py | 测试 support package。 |
| blocking_io/conftest.py | 阻塞 IO 测试 fixture。 |

```mermaid
flowchart TD
  ReplayTests --> ReplayProvider
  RouterTests --> SeedRuns
  BlockingTests --> BlockingConftest
  SupportPackage --> SharedUtils
  ReplayProvider --> Fixtures
  SeedRuns --> TestDB
  BlockingConftest --> BlockbusterGate
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