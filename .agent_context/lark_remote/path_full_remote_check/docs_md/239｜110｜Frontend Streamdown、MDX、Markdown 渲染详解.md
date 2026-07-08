{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>110｜Frontend Streamdown、MDX、Markdown 渲染详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| core/streamdown | Markdown 预处理、插件、Mermaid 支持。 |\n| markdown-content.tsx | workspace 消息 Markdown 渲染。 |\n| mdx-components.ts | Nextra/MDX wrapper 组件。 |\n| rehype | split words、KaTeX、raw HTML 等处理。 |\n| code-editor.tsx | artifact 代码展示。 |\n\n```mermaid\nflowchart TD\n  RawMarkdown --> Preprocess[streamdown preprocess]\n  Preprocess --> Plugins[remark rehype plugins]\n  Plugins --> Mermaid[mermaid handling]\n  Plugins --> Katex[math rendering]\n  Plugins --> Code[code highlighting]\n  Code --> MarkdownContent\n  MDX[MDX page] --> MDXComponents\n  ArtifactText --> CodeEditor\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "CKqhdfJVpoYmIzxl65Gmb15MyCd",
      "revision_id": 16
    }
  }
}
