<title>218｜Replay / Setup / TODO / Plan Mode Docs 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。
</callout>

| 文档点 | 说明 |
|-|-|
| REPLAY_E2E.md | Replay E2E 使用说明。 |
| SETUP.md | 后端 setup 说明。 |
| TODO.md | 待办列表。 |
| plan_mode_usage.md | plan mode 用法。 |
| task_tool_improvements.md | task tool 改进记录。 |

```mermaid
flowchart TD
  ReplayDoc --> ReplayFixtures[record and replay fixtures]
  SetupDoc --> DevSetup[backend setup]
  PlanModeDoc --> TodoMiddleware[TodoMiddleware]
  TaskDoc --> TaskTool[task tool]
  TodoDoc --> Backlog[future improvements]
  ReplayFixtures --> Tests[replay e2e tests]
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
stateDiagram-v2
  [*] --> PENDING : execute_async prompt
  PENDING --> RUNNING : scheduler submits run_task
  RUNNING --> RUNNING : task_running SSE writer
  RUNNING --> COMPLETED : result.result returned
  RUNNING --> FAILED : result.error returned
  RUNNING --> CANCELLED : request_cancel_background_task
  RUNNING --> TIMED_OUT : poll_count exceeds max_poll_count
  RUNNING --> CANCELLED : CancelledError shielded await
  COMPLETED --> [*] : cleanup_background_task
  FAILED --> [*] : cleanup_background_task
  CANCELLED --> [*] : _is_subagent_terminal then cleanup
  TIMED_OUT --> [*] : cleanup_background_task
```