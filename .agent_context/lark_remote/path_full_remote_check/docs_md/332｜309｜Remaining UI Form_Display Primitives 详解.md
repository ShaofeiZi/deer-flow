{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>309｜Remaining UI Form/Display Primitives 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐剩余 frontend/UI/misc 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| carousel.tsx | 轮播组件。 |\n| progress.tsx | 进度展示。 |\n| separator.tsx | 分隔线。 |\n| skeleton.tsx | 骨架屏。 |\n| terminal.tsx | 终端展示。 |\n| number-ticker.tsx | 数字动效。 |\n\n```mermaid\nflowchart TD\n  Data --> NumberTicker\n  Loading --> Skeleton\n  Logs --> Terminal\n  Wizard --> Progress\n  Layout --> Separator\n  Landing --> Carousel\n  Components --> AppUI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "M6Umdnmrson8ICx4QTsmQbNZypb",
      "revision_id": 16
    }
  }
}
