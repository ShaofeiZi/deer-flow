{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>87｜Telegram、DingTalk、WeCom Channel 深入运行逻辑</title>\n\n<callout emoji=\"✅\">\n**本章目标：**进一步细化三个常用外部 IM channel。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Telegram | Bot API update -> TelegramChannel -> send message。 |\n| DingTalk | Stream push，rich text 提取，Markdown 表格转换。 |\n| WeCom | 企业微信智能机器人 SDK/接口。 |\n| 共同抽象 | 继承 Channel，统一 start/stop/send。 |\n\n```mermaid\nflowchart TD\n  Telegram[Telegram update] --> T[TelegramChannel]\n  Ding[DingTalk stream event] --> D[DingTalkChannel]\n  WeCom[WeCom event] --> W[WeComChannel]\n  T --> Normalize[InboundMessage]\n  D --> Rich[extract rich text and adapt markdown]\n  Rich --> Normalize\n  W --> Normalize\n  Normalize --> Manager[ChannelManager]\n  Manager --> Run[Agent run]\n  Run --> Outbound[platform outbound message]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "ADipdPBhKoiHtpxvRr3mo9gHyag",
      "revision_id": 18
    }
  }
}
