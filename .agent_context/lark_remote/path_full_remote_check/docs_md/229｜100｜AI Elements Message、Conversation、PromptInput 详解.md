{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>100｜AI Elements Message、Conversation、PromptInput 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n---\n\n# 可视化增强：前端组件关系图\n\n<callout emoji=\"💡\">\n**图解目标：**补充 AI Elements 组件如何支撑聊天输入、消息展示和操作控件。\n</callout>\n\n## 1. AI Elements 组件关系图\n\n```mermaid\nflowchart TD\n  ChatPage --> Conversation\n  Conversation --> MessageList\n  MessageList --> Message\n  Message --> MarkdownContent\n  Message --> Reasoning\n  Message --> ArtifactPreview\n  ChatPage --> PromptInput\n  PromptInput --> Textarea\n  PromptInput --> Controls\n  Controls --> Submit\n  Controls --> Attachments\n  Message --> Toolbar\n  Toolbar --> Copy\n  Toolbar --> OpenArtifact\n```\n\n| 读图对象 | 图里怎么看 | 维护入口 |\n|-|-|-|\n| 模块职责 | Conversation 管容器，Message 管展示，PromptInput 管输入 | ai-elements components |\n| 数据流 | ChatPage 状态向下传递，用户操作通过 controls 回调向上提交 | frontend components |\n| 阅读路径 | 先看容器，再看消息，再看输入控件 | 100 章节 |\n\n| 模块点 | 说明 |\n|-|-|\n| message.tsx | AI message primitive。 |\n| conversation.tsx | 会话容器和滚动区域。 |\n| prompt-input.tsx | 输入框、textarea、submit、footer。 |\n| controls/toolbar | 输入和消息辅助控制。 |\n\n```mermaid\nflowchart TD\n  ChatPage --> Conversation\n  Conversation --> Message\n  ChatPage --> PromptInput\n  PromptInput --> Textarea\n  PromptInput --> Footer\n  Footer --> Submit\n  Message --> MarkdownContent\n  Toolbar --> MessageActions\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "P3MRdKYHNokBdDxaDl0mRmEcywh",
      "revision_id": 17
    }
  }
}
