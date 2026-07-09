<title>116｜UI Data Display Primitives：Card、Avatar、Item、Table-like 详解</title>

<callout emoji="✅">
**本章目标：**继续按小模块解释职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| card.tsx | 卡片容器。 |
| avatar.tsx | 用户/agent 头像。 |
| item.tsx | 列表项 primitive。 |
| badge.tsx | 状态标识。 |
| empty.tsx | 空状态。 |
| terminal.tsx | 终端风格展示。 |

```mermaid
flowchart TD
  Data --> Card
  User --> Avatar
  List --> Item
  Status --> Badge
  EmptyState --> Empty
  Logs --> Terminal
  Card --> AgentCard
  Item --> Lists
  Badge --> StatusViews
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
  subgraph RouteL["route layer"]
    P["agents/page.tsx"]
  end
  subgraph CoreL["core data layer"]
    H["useAgents"]
    L["listAgents"]
    B["GET /api/agents"]
  end
  subgraph BizL["business component"]
    G["AgentGallery"]
    AC["AgentCard"]
  end
  subgraph UIL["ui primitives"]
    C["Card"]
    CH["CardHeader"]
    CT["CardTitle"]
    CD["CardDescription"]
    BDG["Badge"]
    CF["CardFooter"]
  end
  P --> G
  G --> H
  H --> L
  L --> B
  G --> AC
  AC --> C
  C --> CH
  CH --> CT
  CH --> CD
  AC --> BDG
  C --> CF
```