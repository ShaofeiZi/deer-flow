<title>262｜Runtime Checkpointer Provider 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 persistence/runtime 单文件，说明模型、仓储、provider 的调用关系。
</callout>

| 模块点 | 说明 |
|-|-|
| runtime/checkpointer/provider.py | 同步/基础 provider。 |
| runtime/checkpointer/async_provider.py | 异步上下文 provider。 |
| make_checkpointer | 根据 AppConfig 创建 checkpointer。 |
| run_agent | 执行期间读写 checkpoint。 |

```mermaid
flowchart TD
  AppConfig --> MakeCheckpointer
  MakeCheckpointer --> Checkpointer
  Checkpointer --> RunAgent
  RunAgent --> ReadPreRun[read pre-run checkpoint]
  RunAgent --> WriteState[write graph state]
  Rollback --> Checkpointer
  ThreadsStateAPI --> Checkpointer
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