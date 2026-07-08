{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 223｜AUTO_TITLE / TITLE_GENERATION 文档单独详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆剩余文档/content 模块，说明用途和关联运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| AUTO_TITLE_GENERATION.md | 自动标题功能说明。 |\n| TITLE_GENERATION_IMPLEMENTATION.md | 实现细节。 |\n| TitleMiddleware | 核心实现。 |\n| Thread meta sync | run 收尾同步到会话列表。 |\n\n```mermaid\nflowchart TD\n  Docs --> TitleMiddleware\n  TitleMiddleware --> Prompt[title prompt]\n  Prompt --> Model[LLM or fallback]\n  Model --> State[thread title]\n  State --> ThreadMeta\n  ThreadMeta --> FrontendSidebar\n```",
      "document_id": "HvzydHuWDoAn7KxJi7GmW3DbyCh",
      "revision_id": 18
    }
  }
}
