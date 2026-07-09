<title>69｜Feishu/Slack/Discord/Telegram/WeCom/DingTalk/Wechat Channel 详解</title>

<callout emoji="✅">
**本章目标：**逐个平台讲清输入输出、命令识别和消息适配差异。
</callout>

# 1. 模块职责

| 模块 | 说明 |
|-|-|
| Feishu | WebSocket 事件，流式更新卡片，支持 OK/DONE reaction。 |
| Slack | Socket Mode，处理 bot mention 和 allowed users。 |
| Discord | discord.py bot，支持 mention_only、allowed_channels 和可选 thread_mode。 |
| Telegram | Bot API long polling。 |
| WeCom | 企业微信智能机器人。 |
| DingTalk | Stream Push，Markdown 表格适配。 |
| Wechat | iLink/媒体加解密相关逻辑。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  Inbound[Platform event] --> Normalize[normalize text files metadata]
  Discord[Discord message/thread] --> Normalize
  Normalize --> Command{known command?}
  Command -->|yes| Builtin[handle channel command]
  Command -->|no| Manager[ChannelManager]
  Manager --> Run[Agent run]
  Run --> Format[platform markdown/card formatting]
  Format --> Outbound[send message or update card]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是查找和学习更快，职责更聚焦。 |
| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |
| 重点代码 | 重点代码见本章表格列出的源码路径。 |
| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |

```mermaid
flowchart TD
  Svc[ChannelService.start] --> Loop[ChannelManager._dispatch_loop]
  Svc --> Chan[Channel.start - feishu slack discord telegram wecom dingtalk wechat]
  Chan -->|publish_inbound| Bus[MessageBus inbound queue]
  Bus --> Loop
  Loop --> Hdr[_handle_message semaphore]
  Hdr -->|COMMAND| Cmd[_handle_command - new status models memory help]
  Hdr -->|CHAT| Chat[_handle_chat]
  Chat --> Store[ChannelStore get or create thread]
  Store --> Files[receive_file and ingest_inbound_files]
  Files --> Stream{_channel_supports_streaming}
  Stream -->|feishu wecom| WaitS[runs.stream]
  Stream -->|others| WaitW[runs.wait]
  WaitS --> Prep[extract response text and artifacts]
  WaitW --> Prep
  Prep -->|publish_outbound| Out[MessageBus outbound]
  Cmd --> Out
  Out --> CB[Channel._on_outbound]
  CB --> Send[send and send_file to platform]
```
