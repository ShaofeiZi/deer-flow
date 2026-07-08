{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>67｜Frontend Agents、Blog、I18n、Static Mode 模块详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐前端非 chat 主链路模块：agents、文档/博客、国际化、静态 mock。\n</callout>\n\n# 1. 模块职责\n\n| 对象 | 说明 |\n|-|-|\n| `frontend/src/core/agents/*` | custom agents API 和 hooks。 |\n| `app/workspace/agents/*` | agent gallery/new agent 创建流程。 |\n| `frontend/src/core/i18n/*` | 语言检测、上下文、翻译 hooks。 |\n| `app/[lang]/docs` | Nextra docs 路由。 |\n| `frontend/src/core/static-mode.ts` | 静态演示模式和 mock thread。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Workspace --> Agents[Agents pages]\n  Agents --> AgentsAPI[core agents api]\n  RootLayout --> I18n[I18nProvider]\n  I18n --> Locale[locale detection]\n  DocsRoute[app lang docs] --> Nextra[Nextra importPage]\n  Blog[app blog] --> Content[content posts]\n  Static[static mode] --> MockThreads[static demo threads]\n  MockThreads --> APIClient[static LangGraph client]\n```\n\n# 3. 排障与修改建议\n\n- 先确认调用方和数据源，再改 schema。\n- 涉及用户数据必须确认鉴权和 owner check。\n- 涉及缓存需要同步 invalidate 或 reset。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是查找和学习更快，职责更聚焦。 |\n| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |\n| 重点代码 | 重点代码见本章表格列出的源码路径。 |\n| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "GZsrdYiLLoT05sxERhNmH1v1ycb",
      "revision_id": 17
    }
  }
}
