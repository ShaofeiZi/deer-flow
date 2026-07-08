{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>68｜Channels Service 与 ChannelManager 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 IM channel service 如何启动、统一消息如何转为 LangGraph run。\n</callout>\n\n# 1. 模块职责\n\n| 模块 | 说明 |\n|-|-|\n| `backend/app/channels/service.py` | 启动/停止 ChannelService，按 config 初始化 channels。 |\n| `backend/app/channels/manager.py` | 统一处理 inbound message、slash skill、attachments、artifact delivery。 |\n| `backend/app/channels/message_bus.py` | InboundMessage/OutboundMessage 数据结构和 MessageBus。 |\n| `backend/app/channels/store.py` | channel 状态存储。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Config[channels config] --> Service[ChannelService]\n  Service --> Channels[Feishu Slack Telegram Discord WeCom DingTalk Wechat]\n  Channels --> Bus[MessageBus]\n  Bus --> Manager[ChannelManager]\n  Manager --> Files[ingest inbound files]\n  Manager --> Capability{channel supports streaming?}\n  Capability -->|Feishu WeCom| Stream[LangGraph run stream]\n  Capability -->|others| Wait[LangGraph runs.wait]\n  Stream --> Response[format response and artifacts]\n  Wait --> Response\n  Response --> Bus\n  Bus --> Channels\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**ChannelService 负责按配置启动各 IM 平台适配器，ChannelManager 负责把统一 InboundMessage 转成 DeerFlow thread/run，再把结果和 artifacts 转回平台消息。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 新平台只需实现 `Channel.start/stop/send` 并注册到 `_CHANNEL_REGISTRY`；Manager 复用 thread 映射、slash skill、附件和 artifact 发送逻辑。 |\n| 代价 | 不同平台的长连接、文件下载、markdown/card 能力差异很大；运行路径还会按 `supports_streaming` 分成 stream 与 wait 两类。 |\n| 重点代码 | `backend/app/channels/service.py`、`backend/app/channels/manager.py`、`backend/app/channels/base.py`、各平台 channel 文件。 |\n| 阅读路径 | 先看 `_CHANNEL_REGISTRY` 和 `_CHANNEL_CREDENTIAL_KEYS`，再看 `CHANNEL_CAPABILITIES`，最后追踪 Manager 的 inbound -> run -> outbound。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "EH0IdtUGuoPKQfxql2UmiuiGylu",
      "revision_id": 21
    }
  }
}
