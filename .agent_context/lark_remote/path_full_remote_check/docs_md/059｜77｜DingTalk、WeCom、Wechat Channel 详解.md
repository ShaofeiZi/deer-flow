{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>77｜DingTalk、WeCom、Wechat Channel 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清企业 IM 渠道的消息适配、富文本/媒体处理和出站格式。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| DingTalk | Stream Push、conversation type、Markdown 表格适配。 |\n| WeCom | 企业微信智能机器人。 |\n| Wechat | iLink 客户端、媒体 AES 加解密、CDN 上传。 |\n| 共同点 | 平台事件 -> InboundMessage -> ChannelManager -> OutboundMessage。 |\n\n```mermaid\nflowchart TD\n  Ding[DingTalk event] --> Adapt[platform adapter]\n  WeCom[WeCom event] --> Adapt\n  Wechat[Wechat event and media] --> Adapt\n  Adapt --> Files[optional inbound file reader]\n  Files --> Manager[ChannelManager]\n  Manager --> Agent[Agent run]\n  Agent --> Format[platform-specific markdown/media]\n  Format --> Send[send outbound message]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Gj3fdQukjo9O0txWJUHmiJMnysh",
      "revision_id": 18
    }
  }
}
