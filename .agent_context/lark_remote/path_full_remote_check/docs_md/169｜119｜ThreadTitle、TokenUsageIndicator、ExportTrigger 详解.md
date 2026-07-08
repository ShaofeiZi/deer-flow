{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 119｜ThreadTitle、TokenUsageIndicator、ExportTrigger 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续按 workspace 业务组件讲解职责、输入输出和运行逻辑。\n</callout>\n\n| 组件/文件 | 说明 |\n|-|-|\n| thread-title.tsx | 展示/编辑当前 thread title。 |\n| token-usage-indicator.tsx | 展示 thread token usage。 |\n| export-trigger.tsx | 导出会话。 |\n| streaming-indicator.tsx | 流式运行状态指示。 |\n\n```mermaid\nflowchart TD\n  ThreadState --> ThreadTitle\n  UserEdit --> Rename[useRenameThread]\n  Rename --> ThreadAPI[patch thread]\n  TokenAPI[useThreadTokenUsage] --> TokenUsageIndicator\n  ThreadMessages --> ExportTrigger\n  StreamState --> StreamingIndicator\n  ExportTrigger --> Download[export file]\n```",
      "document_id": "KcKrdsMpDo6qo7xv6prmAo8uyWT",
      "revision_id": 18
    }
  }
}
