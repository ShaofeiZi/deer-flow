{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 289｜Feishu 与 Slack Channel 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 auth/channel/frontend core 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| feishu.py | 飞书事件、卡片更新、命令识别。 |\n| slack.py | Slack Socket Mode、mention 剥离、allowed users。 |\n| manager.py | 两者都转入 ChannelManager。 |\n| message_bus.py | 统一消息结构。 |\n\n```mermaid\nflowchart TD\n  FeishuEvent --> FeishuChannel\n  SlackEvent --> SlackChannel\n  FeishuChannel --> InboundMessage\n  SlackChannel --> InboundMessage\n  InboundMessage --> ChannelManager\n  ChannelManager --> AgentRun\n  AgentRun --> OutboundMessage\n  OutboundMessage --> FeishuChannel\n  OutboundMessage --> SlackChannel\n```",
      "document_id": "Te3lduXKPorQUox92vhmtBoIyrd",
      "revision_id": 18
    }
  }
}
