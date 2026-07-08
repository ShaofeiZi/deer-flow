{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>317｜Artifact Loader / Hooks / Preview 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆更细 backend/frontend/skill scripts 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| core/artifacts/hooks.ts | useArtifactContent。 |\n| core/artifacts/loader.ts | artifact 加载。 |\n| core/artifacts/preview.ts | 预览类型。 |\n| core/artifacts/utils.ts | URL/path 工具。 |\n\n```mermaid\nflowchart TD\n  ArtifactDetail --> UseArtifactContent\n  UseArtifactContent --> Loader\n  Loader --> ArtifactURL\n  ArtifactURL --> Fetch\n  Fetch --> Content\n  Content --> PreviewType\n  PreviewType --> RenderMode\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明前端 UI primitive、workspace 组件或页面模块的职责、状态来源和渲染分支。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 组件边界清晰后，UI 问题可按 props/state/hook/route 快速定位。 |\n| 代价 | 一次交互常跨页面、hook、context 和展示组件，需要按数据流追踪。 |\n| 重点代码 | 标题对应的 `frontend/src/app/`、`frontend/src/components/` 或 `frontend/src/core/` 文件。 |\n| 阅读路径 | 先看组件输入输出，再看状态来源，最后看事件回调如何改变 UI。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "HudZdufZfo2f20xTug3mMvUhyuh",
      "revision_id": 18
    }
  }
}
