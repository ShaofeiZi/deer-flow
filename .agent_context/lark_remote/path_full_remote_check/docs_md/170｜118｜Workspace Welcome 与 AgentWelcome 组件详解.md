{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 118｜Workspace Welcome 与 AgentWelcome 组件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续按 workspace 业务组件讲解职责、输入输出和运行逻辑。\n</callout>\n\n| 组件/文件 | 说明 |\n|-|-|\n| welcome.tsx | 新会话欢迎态、快捷提示。 |\n| agent-welcome.tsx | Agent 页面欢迎/引导。 |\n| mode-hover-guide.tsx | 模式 hover 说明。 |\n| flip-display.tsx | 动态展示效果。 |\n\n```mermaid\nflowchart TD\n  NewThread[isWelcomeMode true] --> Welcome\n  Welcome --> Suggestions[quick prompts]\n  AgentPage --> AgentWelcome\n  InputMode --> ModeHoverGuide\n  Visual --> FlipDisplay\n  Suggestions --> InputBox\n  ModeHoverGuide --> UserChoice\n```",
      "document_id": "ByTKdUjzFoi8RpxBLfgmBRNyyRb",
      "revision_id": 18
    }
  }
}
