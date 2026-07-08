{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 250｜Frontend Rehype / Streamdown / Mermaid 细节详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试 helper、fixtures、frontend content 支持模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| core/rehype | rehype plugin 封装。 |\n| core/streamdown/mermaid.ts | Mermaid 处理。 |\n| plugins.ts | Markdown 插件。 |\n| preprocess.ts | 内容预处理。 |\n| components/workspace/messages/markdown-content.tsx | 渲染入口。 |\n\n```mermaid\nflowchart TD\n  MarkdownText --> Preprocess\n  Preprocess --> StreamdownPlugins\n  StreamdownPlugins --> Rehype\n  StreamdownPlugins --> Mermaid\n  Mermaid --> Diagram\n  Rehype --> HTML\n  HTML --> MarkdownContent\n  Diagram --> MarkdownContent\n```",
      "document_id": "CtRNd6LImoikZmx1YVkmrPeHyJh",
      "revision_id": 18
    }
  }
}
