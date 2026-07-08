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
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```