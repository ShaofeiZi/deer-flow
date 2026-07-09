<title>149｜frontend-design Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**前端页面/组件高质量设计与实现。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `frontend-design` |
| 路径 | `skills/public/frontend-design/SKILL.md` |
| 类型 | frontend design |
| 触发方式 | 任务匹配或显式 `/frontend-design` |

```mermaid
flowchart TD
  User[User task] --> Match[match frontend-design]
  Match --> Read[read skills public frontend-design SKILL md]
  Read --> Workflow[frontend design workflow]
  Workflow --> Tools[use scripts/tools if needed]
  Tools --> Output[deliver result]
  Output --> Memory[agent may continue or summarize]
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
  Route["app/workspace/chats/[thread_id]/page.tsx"] --> CoreHooks["core/threads/hooks.ts useThreadStream"]
  Route --> SkillsHooks["core/skills/hooks.ts useSkills/useEnableSkill"]
  CoreHooks --> APIClient["core/api/api-client.ts getAPIClient"]
  SkillsHooks --> SkillsAPI["core/skills/api.ts enableSkill"]
  SkillsAPI --> APIClient
  APIClient --> Backend["core/config getBackendBaseURL"]
  Route --> BizComp["components/workspace/input-box.tsx InputBox"]
  Route --> MessageList["components/workspace/messages MessageList"]
  BizComp --> AIE["components/ai-elements prompt-input"]
  MessageList --> AIE
  BizComp --> UIPrim["components/ui button card alert"]
  MessageList --> UIPrim
  Route --> ThreadCtx["components/workspace/messages/context ThreadContext"]
  ThreadCtx --> BizComp
```