<title>122｜AgentGallery、AgentCard 与 NewAgent Page 详解</title>

<callout emoji="✅">
**本章目标：**继续按 workspace 业务组件讲解职责、输入输出和运行逻辑。
</callout>

| 组件/文件 | 说明 |
|-|-|
| agent-gallery.tsx | 展示 agents 列表。 |
| agent-card.tsx | 单个 agent 卡片。 |
| app/workspace/agents/new/page.tsx | 新建 agent 引导对话。 |
| core/agents/\* | agents API 和 hooks。 |

```mermaid
flowchart TD
  AgentsPage --> AgentGallery
  AgentGallery --> UseAgents[useAgents]
  UseAgents --> AgentsAPI
  AgentGallery --> AgentCard
  NewAgentPage --> NameStep[agent name step]
  NameStep --> CheckName[checkAgentName]
  CheckName --> ChatStep[bootstrap chat]
  ChatStep --> SetupAgentTool[setup_agent tool]
  SetupAgentTool --> GetAgent[getAgent retry]
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
flowchart LR
  Card["AgentCard handleDelete"] --> Mut["useDeleteAgent"]
  Mut --> Fn["deleteAgent name"]
  Fn --> Del["DELETE api/agents/name"]
  Del --> Inv["onSuccess invalidate agents"]
  Inv --> Ref["useAgents refetch"]
  Ref --> List["listAgents"]
  List --> Get["GET api/agents"]
  Get --> Gal["AgentGallery re-render"]
```