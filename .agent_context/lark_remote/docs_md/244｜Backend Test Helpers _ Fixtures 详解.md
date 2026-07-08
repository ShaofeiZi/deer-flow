<title>244｜Backend Test Helpers / Fixtures 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试 helper、fixtures、frontend content 支持模块。
</callout>

| 模块点 | 说明 |
|-|-|
| \_agent_e2e_helpers.py | agent E2E 辅助。 |
| \_router_auth_helpers.py | router auth 测试辅助。 |
| \_run_message_pagination_helpers.py | run message 分页辅助。 |
| \_replay_fixture.py | replay fixture 辅助。 |
| conftest.py | pytest 全局 fixture。 |

```mermaid
flowchart TD
  Tests --> Conftest
  Tests --> AgentHelpers
  Tests --> AuthHelpers
  Tests --> PaginationHelpers
  Tests --> ReplayFixture
  Conftest --> Fixtures
  AuthHelpers --> TestClient
  PaginationHelpers --> RunMessages
  ReplayFixture --> ReplayTests
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块承担 agent 扩展能力，是为了把工具、知识、长期上下文或执行环境做成可组合部件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可扩展、可配置、可替换。 |
| 代价 | 代价是配置、prompt、工具 schema、外部服务任一环节出错都会影响结果。 |
| 重点代码 | 重点代码在 `backend/packages/harness/deerflow` 下对应 skills/mcp/memory/sandbox/tools/models 模块。 |
| 阅读路径 | 阅读路径：明确它给 agent 增加了什么能力，以及该能力在哪里被注入。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```