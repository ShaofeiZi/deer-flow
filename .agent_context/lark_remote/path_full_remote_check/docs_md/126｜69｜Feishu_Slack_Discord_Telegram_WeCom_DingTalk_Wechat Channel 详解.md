{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>69｜Feishu/Slack/Discord/Telegram/WeCom/DingTalk/Wechat Channel 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**逐个平台讲清输入输出、命令识别和消息适配差异。\n</callout>\n\n# 1. 模块职责\n\n| 模块 | 说明 |\n|-|-|\n| Feishu | WebSocket 事件，流式更新卡片，支持 OK/DONE reaction。 |\n| Slack | Socket Mode，处理 bot mention 和 allowed users。 |\n| Discord | discord.py bot，支持 mention_only、allowed_channels 和可选 thread_mode。 |\n| Telegram | Bot API long polling。 |\n| WeCom | 企业微信智能机器人。 |\n| DingTalk | Stream Push，Markdown 表格适配。 |\n| Wechat | iLink/媒体加解密相关逻辑。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Inbound[Platform event] --> Normalize[normalize text files metadata]\n  Discord[Discord message/thread] --> Normalize\n  Normalize --> Command{known command?}\n  Command -->|yes| Builtin[handle channel command]\n  Command -->|no| Manager[ChannelManager]\n  Manager --> Run[Agent run]\n  Run --> Format[platform markdown/card formatting]\n  Format --> Outbound[send message or update card]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是查找和学习更快，职责更聚焦。 |\n| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |\n| 重点代码 | 重点代码见本章表格列出的源码路径。 |\n| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "R63yd6XPyoTIaCxrHgKmzacOyoh",
      "revision_id": 17
    }
  }
}
