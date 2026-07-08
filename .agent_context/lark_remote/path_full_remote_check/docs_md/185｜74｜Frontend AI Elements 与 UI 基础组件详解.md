{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>74｜Frontend AI Elements 与 UI 基础组件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 ai-elements 与 workspace UI 基础组件如何支撑聊天体验。\n</callout>\n\n# 1. 模块职责\n\n| 模块 | 说明 |\n|-|-|\n| ai-elements | message、conversation、prompt-input、artifact、reasoning、task、sources 等 AI UI primitive。 |\n| ui components | button、dialog、sidebar、scroll-area、select 等 shadcn/radix 风格组件。 |\n| workspace components | 在 ai-elements 和 ui 基础上组合业务 UI。 |\n| streamdown | Markdown、Mermaid、KaTeX、代码高亮渲染。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Design[UI primitives] --> UI[components ui]\n  AI[AI Elements] --> Workspace[workspace components]\n  UI --> Workspace\n  Streamdown[core streamdown] --> Markdown[MarkdownContent]\n  Markdown --> Message[MessageListItem]\n  Prompt[PromptInput] --> InputBox\n  Artifact[AI artifact primitives] --> ArtifactPanel\n  Workspace --> ChatPage\n```",
      "document_id": "W4CkdRccMosnvWxg22vmYZhcyod",
      "revision_id": 18
    }
  }
}
