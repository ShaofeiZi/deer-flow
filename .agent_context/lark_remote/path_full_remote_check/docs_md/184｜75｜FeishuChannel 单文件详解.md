{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 75｜FeishuChannel 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清飞书渠道如何收消息、开 run、流式更新卡片。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| 命令识别 | `_is_feishu_command` 判断飞书命令。 |\n| Channel 类 | `FeishuChannel` 连接飞书 WebSocket/事件。 |\n| 消息更新 | 运行中更新同一张 in-thread card。 |\n| 反应流 | 保留 OK/DONE reaction 语义。 |\n\n```mermaid\nsequenceDiagram\n  participant Feishu as Feishu Event\n  participant Channel as FeishuChannel\n  participant Manager as ChannelManager\n  participant Run as LangGraph Run\n  participant Card as Feishu Card\n  Feishu->>Channel: inbound message\n  Channel->>Manager: InboundMessage\n  Manager->>Run: stream run\n  Run-->>Manager: chunks\n  Manager-->>Channel: Outbound update\n  Channel->>Card: patch same message card\n```",
      "document_id": "FmyedWaiuoqW75xBkQ9mxXAkyee",
      "revision_id": 18
    }
  }
}
