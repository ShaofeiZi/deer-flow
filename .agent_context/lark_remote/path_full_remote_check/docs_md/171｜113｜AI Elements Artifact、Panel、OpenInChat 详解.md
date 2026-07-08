{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 113｜AI Elements Artifact、Panel、OpenInChat 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续按小模块解释职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| artifact.tsx | artifact primitive。 |\n| panel.tsx | 侧边面板 primitive。 |\n| open-in-chat.tsx | 在聊天中打开/引用。 |\n| context.tsx | AI element context。 |\n\n```mermaid\nflowchart TD\n  ArtifactState --> Artifact\n  Artifact --> Panel\n  Panel --> Detail\n  OpenInChat --> ChatContext\n  Context --> Artifact\n  Context --> Panel\n  Detail --> UserAction\n  UserAction --> ChatMessage\n```",
      "document_id": "JYEIdPqTyo7gqGxXYhGmR1Rpysg",
      "revision_id": 18
    }
  }
}
