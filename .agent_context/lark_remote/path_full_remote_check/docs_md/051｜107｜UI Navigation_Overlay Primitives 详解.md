{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>107｜UI Navigation/Overlay Primitives 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| breadcrumb.tsx | 路径导航。 |\n| dropdown-menu.tsx | 下拉菜单。 |\n| hover-card.tsx | 悬浮卡。 |\n| sheet.tsx | 抽屉。 |\n| tabs.tsx | 标签页。 |\n| collapsible.tsx | 折叠区域。 |\n\n```mermaid\nflowchart TD\n  Navigation --> Breadcrumb\n  Actions --> DropdownMenu\n  HoverInfo --> HoverCard\n  MobilePanel --> Sheet\n  Sections --> Tabs\n  Expandable --> Collapsible\n  Workspace --> Navigation\n  Settings --> Tabs\n  Sidebar --> Collapsible\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明前端 UI primitive、workspace 组件或页面模块的职责、状态来源和渲染分支。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 组件边界清晰后，UI 问题可按 props/state/hook/route 快速定位。 |\n| 代价 | 一次交互常跨页面、hook、context 和展示组件，需要按数据流追踪。 |\n| 重点代码 | 标题对应的 `frontend/src/app/`、`frontend/src/components/` 或 `frontend/src/core/` 文件。 |\n| 阅读路径 | 先看组件输入输出，再看状态来源，最后看事件回调如何改变 UI。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "CIhNdlSJaooYULxICc5mGrLVyvf",
      "revision_id": 18
    }
  }
}
