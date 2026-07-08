<title>328｜Frontend Agents New Route 深拆</title>

<callout emoji="✅">
**本章目标：**继续拆 remaining route/content/docker/script 内部模块。
</callout>

| 模块点 | 说明 |
|-|-|
| agents/new/page.tsx | 自定义 agent 创建向导。 |
| name step | 输入/校验 agent 名称。 |
| chat step | bootstrap agent 对话。 |
| setup_agent tool | 后端创建 agent 文件。 |
| retry getAgent | 写入后轮询读取 agent。 |

```mermaid
flowchart TD
  NewAgentPage --> NameStep
  NameStep --> CheckName
  CheckName --> ChatStep
  ChatStep --> useThreadStream
  useThreadStream --> SetupAgentTool
  SetupAgentTool --> AgentFiles
  AgentFiles --> GetAgentRetry
  GetAgentRetry --> AgentCreated
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 好处是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 坏处是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```