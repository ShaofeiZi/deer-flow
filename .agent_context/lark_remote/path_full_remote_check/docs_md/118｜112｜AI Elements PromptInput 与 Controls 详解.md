{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>112｜AI Elements PromptInput 与 Controls 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续按小模块解释职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| prompt-input.tsx | 输入框 primitive：textarea/footer/submit。 |\n| prompt-input.tsx | 输入框 primitive，内部包含 textarea、footer、submit、attachment、action menu 和 controller/context。 |\n| controls.tsx | React Flow graph controls primitive，不是聊天输入控制按钮。 |\n| toolbar.tsx | React Flow NodeToolbar primitive，用于图节点工具条。 |\n| queue.tsx | 排队/状态展示。 |\n\n```mermaid\nflowchart TD\n  InputBox --> PromptInput\n  PromptInput --> Textarea\n  PromptInput --> Footer\n  Footer --> Submit\n  Footer --> PromptInputSubmit\n  Footer --> PromptInputTools\n  PromptInputTools --> Attach[attachments/action menu]\n  InputBox --> ModeControls[mode/model/reasoning controls]\n  ReactFlow --> Controls[graph controls]\n  ReactFlow --> Toolbar[node toolbar]\n  Queue --> Status\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```\n\n<callout emoji=\"💡\">\n聊天输入的附件、模式、提交按钮不要从 `controls.tsx` 读起；应从 `prompt-input.tsx` 和业务层 `components/workspace/input-box.tsx` 追踪。\n</callout>",
      "document_id": "H9WgdlSXCo9u2oxk5cfmlZCdyMg",
      "revision_id": 18
    }
  }
}
