<title>166｜claude-to-deerflow Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**通过 DeerFlow HTTP API 与正在运行的 DeerFlow 实例交互：健康检查、创建 thread、流式 run、列出 models/skills/agents、管理 memory、上传文件和委派研究任务。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `claude-to-deerflow` |
| 路径 | `skills/public/claude-to-deerflow/SKILL.md` |
| 类型 | DeerFlow HTTP API / LangGraph-compatible runtime client |
| 触发方式 | 用户提到 DeerFlow、要向 DeerFlow 发消息、检查状态、管理模型/skills/agents/memory、上传文件，或显式 `/claude-to-deerflow` |

```mermaid
flowchart TD
  User[User task] --> Resolve[resolve DEERFLOW_URL / GATEWAY / LANGGRAPH env]
  Resolve --> Health[GET Gateway /health]
  Resolve --> Thread[POST LangGraph /threads]
  Thread --> Stream[POST /threads/:id/runs/stream]
  Stream --> SSE[metadata / values / messages-tuple / end]
  Resolve --> Ops[models skills agents memory uploads]
  SSE --> Output[collect final answer or stream events]
  Ops --> Output
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```