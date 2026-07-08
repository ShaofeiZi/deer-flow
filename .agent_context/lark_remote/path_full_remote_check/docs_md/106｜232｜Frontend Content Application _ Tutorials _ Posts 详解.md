{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>232｜Frontend Content Application / Tutorials / Posts 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化 content/spec/docs 单模块，补充运行/维护逻辑图。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| application | 应用场景文档。 |\n| tutorials | 教程。 |\n| posts | 博客文章内容。 |\n| blog core | getAllPosts / getBlogIndexData。 |\n| tags | 按 tag 聚合。 |\n\n```mermaid\nflowchart TD\n  Application --> DocsSite\n  Tutorials --> DocsSite\n  Posts --> BlogCore\n  BlogCore --> PostList\n  BlogCore --> Tags\n  Tags --> TagPage\n  PostList --> BlogLayout\n  DocsSite --> User\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块把 MDX 内容、博客文章、标签聚合和多语言偏好接到 Nextra/Next.js 页面上。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 内容文件和页面逻辑分离，文章可以按语言、slug、tag 聚合展示。 |\n| 代价 | route 归一化、语言回退和 tag slug 需要和页面路径保持一致。 |\n| 重点代码 | `frontend/src/core/blog/index.ts`、`frontend/src/app/blog/posts/page.tsx`、`frontend/src/app/blog/tags/[tag]/page.tsx`、`frontend/src/content/*/posts`。 |\n| 阅读路径 | 先看 content 目录，再看 `getAllPosts` 如何合并语言版本，最后看 posts/tags 页面如何消费 `getBlogIndexData`。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```\n\n```mermaid\nflowchart TD\n  ContentPosts[content zh/en posts] --> PageMap[getPageMap]\n  PageMap --> BlogCore[getAllPosts]\n  BlogCore --> LangMerge[preferred language merge]\n  LangMerge --> Tags[tag aggregation]\n  LangMerge --> PostsPage[All Posts page]\n  Tags --> TagPage[Tag page]\n```",
      "document_id": "ZnBVdCkwToJYgHxr19qm9NmcyZe",
      "revision_id": 18
    }
  }
}
