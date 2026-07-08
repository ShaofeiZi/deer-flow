{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 104｜AI Elements CodeBlock、WebPreview、Canvas、Image 详解\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| code-block.tsx | 代码块展示、高亮和复制。 |\n| web-preview.tsx | 网页/HTML 预览容器。 |\n| canvas.tsx | Canvas 类 AI 产物展示。 |\n| image.tsx | 图片元素展示。 |\n| artifact.tsx | 与 artifact panel 形成更高层封装。 |\n\n```mermaid\nflowchart TD\n  AssistantContent --> CodeBlock\n  AssistantContent --> Image\n  AssistantContent --> Canvas\n  ArtifactFile --> WebPreview\n  CodeBlock --> Copy[copy action]\n  WebPreview --> IFrame[iframe or preview]\n  Image --> Render[image display]\n  Canvas --> Visual[canvas render]\n```",
      "document_id": "TJC7dR82Hou6xdxRBTmmuJR2yBe",
      "revision_id": 18
    }
  }
}
