{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 85｜Feishu Channel 深入运行逻辑\n\n<callout emoji=\"✅\">\n**本章目标：**进一步细化 Feishu channel 的卡片更新、reaction 和 thread 映射。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| 入口 | Feishu event -> FeishuChannel -> ChannelManager。 |\n| 命令 | 识别内置命令和 slash skill。 |\n| 运行 | Feishu 采用 runs.stream，边生成边更新卡片。 |\n| 状态 | 保存 running card message_id，直到 run 完成。 |\n| 交互 | OK/DONE reaction 流程保持。 |\n\n```mermaid\nsequenceDiagram\n  participant F as Feishu\n  participant C as FeishuChannel\n  participant M as ChannelManager\n  participant R as runs.stream\n  participant Card as Feishu Card\n  F->>C: message event\n  C->>M: normalized inbound\n  M->>R: create stream run\n  R-->>M: message chunks and values\n  M-->>C: incremental text/artifacts\n  C->>Card: patch existing card\n  R-->>M: final state\n  C->>Card: mark done and reaction flow\n```",
      "document_id": "CjJDdvrq1o4xqdxx1m1mQM7Vyth",
      "revision_id": 18
    }
  }
}
