<title>63｜feedback、suggestions、channels Router 详解</title>

<callout emoji="✅">
**本章目标：**讲清反馈、跟进建议和 IM channel 管理这些辅助 router。
</callout>

# 1. 模块职责

| 对象 | 说明 |
|-|-|
| `feedback.py` | run feedback CRUD、upsert、stats。 |
| `suggestions.py` | 根据最近对话生成 follow-up suggestions。 |
| `channels.py` | 查询/重启 IM channel service。 |
| `feedback stats` | 按 run 汇总反馈。 |
| `think block strip` | suggestions 解析前剥离 reasoning <think>。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  FeedbackUI[Feedback UI] --> FeedbackRouter[feedback.py]
  FeedbackRouter --> Repo[FeedbackRepository]
  ChatUI[Chat UI] --> Suggest[suggestions.py]
  Suggest --> Strip[strip think blocks]
  Strip --> Model[LLM generate JSON list]
  Model --> Parse[parse suggestions]
  Admin[Admin UI] --> Channels[channels.py]
  Channels --> Service[channel service status restart]
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