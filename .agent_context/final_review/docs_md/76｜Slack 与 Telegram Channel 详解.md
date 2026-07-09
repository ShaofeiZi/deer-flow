<title>76｜Slack 与 Telegram Channel 详解</title>

<callout emoji="✅">
**本章目标：**讲清 Slack Socket Mode 与 Telegram Bot API 如何复用 ChannelManager。
</callout>

| 模块点 | 说明 |
|-|-|
| Slack | 剥离 bot mention，allowed users，Socket Mode。 |
| Telegram | Bot API long polling，收发文本。 |
| 共同点 | 都转换为 InboundMessage，再走 ChannelManager。 |
| 差异 | Slack/Telegram 仍更多走最终 wait response path。 |

```mermaid
flowchart TD
  SlackEvent[Slack event] --> Slack[SlackChannel]
  TelegramEvent[Telegram update] --> Telegram[TelegramChannel]
  Slack --> Normalize[normalize text and user]
  Telegram --> Normalize
  Normalize --> Manager[ChannelManager]
  Manager --> Run[LangGraph run]
  Run --> Out[OutboundMessage]
  Out --> SlackSend[Slack send]
  Out --> TelegramSend[Telegram send]
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
sequenceDiagram
  participant Slack as SlackChannel
  participant TG as TelegramChannel
  participant Bus as MessageBus
  participant Mgr as ChannelManager
  participant GW as Gateway

  Slack->>Slack: _on_socket_event strip mention check users
  Slack->>Slack: _send_running_reply Working on it
  Slack->>Bus: publish_inbound InboundMessage
  TG->>TG: _on_text _check_user strip username
  TG->>TG: _send_running_reply Working on it
  TG->>Bus: publish_inbound InboundMessage
  Bus->>Mgr: _dispatch_loop get_inbound
  Mgr->>Mgr: _handle_chat _resolve_run_params
  Mgr->>Mgr: store get_thread_id reuse or create
  Mgr->>GW: runs.wait thread_id human_message
  GW-->>Mgr: result messages
  Mgr->>Mgr: _extract_response_text _extract_artifacts
  Mgr->>Bus: publish_outbound OutboundMessage
  Bus->>Slack: _on_outbound chat_postMessage
  Bus->>TG: _on_outbound bot send_message
```