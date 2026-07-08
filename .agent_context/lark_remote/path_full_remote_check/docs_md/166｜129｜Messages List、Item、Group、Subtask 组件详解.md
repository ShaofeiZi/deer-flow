{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 129｜Messages List、Item、Group、Subtask 组件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| message-list.tsx | 消息列表、历史加载、分组渲染。 |\n| message-list-item.tsx | 单条消息。 |\n| message-group.tsx | processing/reasoning/tool calls。 |\n| subtask-card.tsx | task tool 状态。 |\n| message-token-usage.tsx | 消息级 token usage。 |\n\n```mermaid\nflowchart TD\n  ThreadMessages --> MessageList\n  MessageList --> Groups[getMessageGroups]\n  Groups --> Item[MessageListItem]\n  Groups --> Group[MessageGroup]\n  Groups --> Subtask[SubtaskCard]\n  Groups --> TokenUsage[MessageTokenUsage]\n  History[load more] --> MessageList\n  SubtaskEvents --> SubtaskCard\n```",
      "document_id": "LX5PdYmtKoUkRmxdegZmkAj8ySb",
      "revision_id": 18
    }
  }
}
