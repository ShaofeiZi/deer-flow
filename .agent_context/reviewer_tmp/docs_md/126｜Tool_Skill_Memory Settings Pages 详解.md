<title>126｜Tool、Skill、Memory Settings Pages 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| tool-settings-page.tsx | MCP tools 列表和启停。 |
| skill-settings-page.tsx | skills 列表、分类、启停、创建 skill。 |
| memory-settings-page.tsx | memory summaries/facts、CRUD、导入导出。 |
| core hooks | useMCPConfig/useSkills/useMemory。 |

```mermaid
flowchart TD
  SettingsDialog --> ToolPage
  SettingsDialog --> SkillPage
  SettingsDialog --> MemoryPage
  ToolPage --> MCPAPI[GET PUT api mcp config]
  SkillPage --> SkillsAPI[GET PUT api skills]
  SkillPage --> CreateSkill[route new chat mode skill]
  MemoryPage --> MemoryAPI[api memory facts CRUD]
  MemoryAPI --> QueryCache[React Query cache]
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