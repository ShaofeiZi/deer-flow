<title>185｜Channels / Community Provider Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| test_channels.py | channel manager/service。 |
| test_feishu_parser/dingtalk/slack/telegram/discord | 平台 channel。 |
| test_ddg/exa/firecrawl/infoquest/jina/serper | community providers。 |
| test_channel_file_attachments.py | 入站文件附件。 |

```mermaid
flowchart TD
  Channels --> ChannelTests
  PlatformAdapters --> PlatformTests
  CommunityProviders --> ProviderTests
  Attachments --> AttachmentTests
  ChannelTests --> InboundOutbound[Inbound/Outbound Message]
  ProviderTests --> MockExternal[mocked external API]
  AttachmentTests --> FileIngest[file ingest]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
sequenceDiagram
  participant Platform as FeishuChannel
  participant Bus as MessageBus
  participant Mgr as ChannelManager
  participant Store as ChannelStore
  participant GW as Gateway client

  Platform->>Bus: publish_inbound InboundMessage
  Bus->>Mgr: get_inbound dispatch_loop
  Mgr->>Mgr: _handle_message route chat or command
  Mgr->>Store: get_thread_id by topic_id
  alt thread missing
    Mgr->>GW: threads.create
    GW-->>Mgr: thread_id
    Mgr->>Store: set_thread_id
  end
  opt msg.files present
    Mgr->>Platform: receive_file
  end
  Mgr->>GW: runs.wait human_message
  GW-->>Mgr: result with messages
  Mgr->>Mgr: _extract_response_text and _extract_artifacts
  Mgr->>Bus: publish_outbound OutboundMessage
  Bus->>Platform: _on_outbound callback
  Platform->>Platform: send then send_file
```