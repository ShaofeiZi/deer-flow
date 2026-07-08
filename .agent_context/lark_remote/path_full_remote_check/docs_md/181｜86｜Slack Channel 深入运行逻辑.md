{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 86｜Slack Channel 深入运行逻辑\n\n<callout emoji=\"✅\">\n**本章目标：**进一步细化 Slack Socket Mode、mention 剥离、allowed users 和回复逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Socket Mode | 通过 Slack SDK 接收事件。 |\n| mention 处理 | 剥离 leading bot mention。 |\n| allowed users | 限制可调用用户集合。 |\n| 消息归一 | 转为 InboundMessage。 |\n| 输出 | 把 agent 最终响应发送回 Slack。 |\n\n```mermaid\nflowchart TD\n  SlackEvent[Slack Socket event] --> Channel[SlackChannel]\n  Channel --> Mention[strip bot mention]\n  Mention --> Allowed{allowed user?}\n  Allowed -->|no| Ignore[ignore or reject]\n  Allowed -->|yes| Inbound[InboundMessage]\n  Inbound --> Manager[ChannelManager]\n  Manager --> Run[Agent run]\n  Run --> Format[Slack markdown]\n  Format --> Send[Slack response]\n```",
      "document_id": "V9S3dU4Npoer4hxYDKomIVBeyVh",
      "revision_id": 18
    }
  }
}
