<title>291｜WeCom 与 Wechat Channel 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 auth/channel/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| wecom.py | 企业微信机器人 channel。 |
| wechat.py | Wechat/iLink、媒体加解密、CDN 上传。 |
| Inbound files | 入站文件读取。 |
| Outbound media | 出站媒体处理。 |

```mermaid
flowchart TD
  WeComEvent --> WeComChannel
  WechatEvent --> WechatChannel
  WechatChannel --> AES[media AES decrypt encrypt]
  WechatChannel --> CDN[media upload]
  WeComChannel --> InboundMessage
  CDN --> OutboundMessage
  InboundMessage --> ChannelManager
  OutboundMessage --> PlatformSend
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**WeCom/Wechat channel 把不同 IM 协议收敛成统一的 `MessageBus` 入站/出站消息，再交给 `ChannelManager` 调用 DeerFlow 运行时。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | WeCom WebSocket、Wechat iLink long-poll、附件读取和出站回复都能复用同一套 channel manager 分派逻辑。 |
| 代价 | WeCom 依赖 SDK 的 WebSocket/media upload 能力，Wechat 依赖 iLink cursor、AES/CDN 和本地下载目录，附件处理需要按 channel 分支读取。 |
| 重点代码 | `backend/app/channels/wecom.py`、`backend/app/channels/wechat.py`、`backend/app/channels/manager.py`、`backend/app/channels/service.py`。 |
| 阅读路径 | 先看 `ChannelService` 如何加载 channel，再看 channel 入站回调如何 publish inbound，最后看 `ChannelManager` 如何读取附件并把结果发回 outbound。 |

```mermaid
flowchart TD
  Service[ChannelService] --> WeCom[WeComChannel]
  Service --> Wechat[WechatChannel]
  WeCom --> Bus[MessageBus inbound/outbound]
  Wechat --> Bus
  Bus --> Manager[ChannelManager]
  Manager --> Runtime[LangGraph/Gateway run]
  Runtime --> Outbound[OutboundMessage]
  Outbound --> WeCom
  Outbound --> Wechat
```