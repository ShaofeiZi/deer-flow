<title>290｜Telegram、DingTalk、Discord Channel 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 auth/channel/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| telegram.py | Telegram Bot API。 |
| dingtalk.py | DingTalk Stream Push、Markdown 适配。 |
| discord.py | Discord channel。 |
| base.py | Channel 抽象。 |

```mermaid
flowchart TD
  TelegramUpdate --> TelegramChannel
  DingTalkEvent --> DingTalkChannel
  DiscordEvent --> DiscordChannel
  TelegramChannel --> BaseChannel
  DingTalkChannel --> BaseChannel
  DiscordChannel --> BaseChannel
  BaseChannel --> MessageBus
  MessageBus --> ChannelManager
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这些 channel adapter 把不同 IM 平台的事件协议收敛成统一 `InboundMessage`，再通过 `MessageBus` 交给 `ChannelManager`。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 平台差异被限制在 adapter 内，运行层只处理统一消息和附件结构。 |
| 代价 | 每个平台的鉴权、长连接、thread/topic、文件上传能力不同，adapter 需要分别处理。 |
| 重点代码 | `backend/app/channels/telegram.py`、`backend/app/channels/dingtalk.py`、`backend/app/channels/discord.py`、`backend/app/channels/base.py`、`backend/app/channels/message_bus.py`、`backend/app/channels/manager.py`。 |
| 阅读路径 | 先看 channel 如何产生 InboundMessage，再看 ChannelManager 如何启动 run，最后看 OutboundMessage 如何回到平台。 |

```mermaid
sequenceDiagram
  participant TG as TelegramChannel
  participant DT as DingTalkChannel
  participant DC as DiscordChannel
  participant Bus as MessageBus
  participant Mgr as ChannelManager
  participant Store as ChannelStore
  participant GW as Gateway
  Note over TG,DC: each adapter runs polling or stream in own thread
  TG->>Bus: publish_inbound InboundMessage
  DT->>Bus: publish_inbound InboundMessage
  DC->>Bus: publish_inbound InboundMessage
  Bus->>Mgr: get_inbound in dispatch_loop
  Mgr->>Store: get_thread_id chat_id topic_id
  alt no existing thread
    Mgr->>GW: threads.create
    Mgr->>Store: set_thread_id
  end
  alt supports_streaming
    Mgr->>GW: runs.stream
    GW-->>Mgr: stream chunks
    Mgr->>Bus: publish_outbound is_final false
  else non-streaming
    Mgr->>GW: runs.wait
    GW-->>Mgr: final state
  end
  Mgr->>Bus: publish_outbound OutboundMessage final
  Bus->>TG: _on_outbound
  Bus->>DT: _on_outbound
  Bus->>DC: _on_outbound
  Note over TG,DC: base._on_outbound filters by channel_name then send and send_file
```