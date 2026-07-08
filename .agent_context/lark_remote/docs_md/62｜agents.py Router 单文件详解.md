<title>62｜agents.py Router 单文件详解</title>

<callout emoji="✅">
**本章目标：**讲清 custom agents API、agent config/SOUL 读写和用户 profile。
</callout>

# 1. 模块职责

| 对象 | 说明 |
|-|-|
| `list_agents` | 列出自定义 agent。 |
| `check_agent_name` | 校验名称合法性和冲突。 |
| `create_agent_endpoint` | 创建 agent config 和 SOUL。 |
| `update_agent/delete_agent` | 更新/删除自定义 agent。 |
| `user_profile` | 读取和更新用户 profile。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  UI[Agent Gallery] --> API[agents.py]
  API --> Enabled{agents api enabled?}
  Enabled --> Name[validate and normalize name]
  Name --> Dir[resolve agent dir per user]
  Dir --> Config[AGENT config]
  Dir --> Soul[SOUL md]
  Config --> Response[AgentResponse]
  Soul --> Response
  Update[update/delete] --> Dir
```

# 3. 排障与修改建议

- 先确认调用方和数据源，再改 schema。
- 涉及用户数据必须确认鉴权和 owner check。
- 涉及缓存需要同步 invalidate 或 reset。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块采用 router/API 分层，是为了把 HTTP 边界、鉴权、请求响应模型和内部服务逻辑分开。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是接口职责清晰，前端和外部 SDK 可稳定调用。 |
| 代价 | 代价是一次业务流常跨 router、service、runtime、repository 多层。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/` 与 `backend/app/gateway/services.py`。 |
| 阅读路径 | 阅读路径：从 URL 路径找 router，再看 request model、authz、依赖注入和 service 调用。 |

```mermaid
flowchart TD
  A[设计动机] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[理解方式]
```