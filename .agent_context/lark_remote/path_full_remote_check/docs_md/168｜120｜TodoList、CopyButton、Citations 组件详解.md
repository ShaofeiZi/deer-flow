{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 120｜TodoList、CopyButton、Citations 组件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续按 workspace 业务组件讲解职责、输入输出和运行逻辑。\n</callout>\n\n| 组件/文件 | 说明 |\n|-|-|\n| todo-list.tsx | 展示 thread.values.todos。 |\n| copy-button.tsx | 复制消息/代码内容。 |\n| citations/citation-link.tsx | 渲染引用链接。 |\n| citations/artifact-link.tsx | 把 artifact path 转成可点击链接。 |\n\n```mermaid\nflowchart TD\n  ThreadValues[todos] --> TodoList\n  Message --> CopyButton\n  MessageContent --> CitationParser\n  CitationParser --> CitationLink\n  ArtifactPath --> ArtifactLink\n  ArtifactLink --> ArtifactAPI\n  CopyButton --> Clipboard\n```",
      "document_id": "UIbqdws4zoEH78xfssBmvIPeywd",
      "revision_id": 18
    }
  }
}
