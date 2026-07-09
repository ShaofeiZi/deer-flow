<title>63｜feedback、suggestions、channels Router 详解</title>

<callout emoji="✅">
**本章目标：**讲清反馈、跟进建议和 IM channel 管理这些辅助 router。
</callout>

# 1. 模块职责

| 对象 | 说明 |
|-|-|
| `backend/app/gateway/routers/feedback.py` | run feedback CRUD、upsert、stats。 |
| `backend/app/gateway/routers/suggestions.py` | 根据最近对话生成 follow-up suggestions。 |
| `backend/app/gateway/routers/channels.py` | 查询/重启 IM channel service。 |
| `feedback stats` | 按 run 汇总反馈。 |
| `think block strip` | suggestions 解析前剥离 reasoning <think>。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  FeedbackUI[Feedback UI] --> FeedbackRouter[backend/app/gateway/routers/feedback.py]
  FeedbackRouter --> Repo[FeedbackRepository]
  ChatUI[Chat UI] --> Suggest[backend/app/gateway/routers/suggestions.py]
  Suggest --> Strip[strip think blocks]
  Strip --> Model[LLM generate JSON list]
  Model --> Parse[parse suggestions]
  Admin[Admin UI] --> Channels[backend/app/gateway/routers/channels.py]
  Channels --> Service[channel service status restart]
```

# 3. 排障与修改建议

- 先确认调用方和数据源，再改 schema。
- 涉及用户数据必须确认鉴权和 owner check。
- 涉及缓存需要同步 invalidate 或 reset。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |
| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |
| 重点代码 | 标题对应的源码、测试或文档入口。 |
| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |

```mermaid
flowchart TD
  A[设计目的] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```
