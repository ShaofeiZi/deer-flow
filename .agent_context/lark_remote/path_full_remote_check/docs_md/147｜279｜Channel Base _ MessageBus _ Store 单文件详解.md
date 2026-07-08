{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 279｜Channel Base / MessageBus / Store 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 channels/auth/frontend core 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| base.py | Channel 抽象基类。 |\n| message_bus.py | InboundMessage/OutboundMessage/MessageBus。 |\n| store.py | ChannelStore。 |\n| commands.py | 已知 channel 命令识别。 |\n\n```mermaid\nflowchart TD\n  PlatformChannel --> ChannelBase\n  ChannelBase --> MessageBus\n  MessageBus --> InboundMessage\n  MessageBus --> OutboundMessage\n  InboundMessage --> ChannelManager\n  OutboundMessage --> PlatformChannel\n  ChannelStore --> ChannelState\n  Commands --> ChannelManager\n```",
      "document_id": "TYXmdsPIjoMwwWxzLzzm8SQWync",
      "revision_id": 18
    }
  }
}
