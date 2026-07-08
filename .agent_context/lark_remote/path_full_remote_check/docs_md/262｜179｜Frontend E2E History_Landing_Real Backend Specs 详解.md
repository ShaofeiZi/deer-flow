{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>179｜Frontend E2E History/Landing/Real Backend Specs 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| thread-history.spec.ts | 历史消息。 |\n| thread-history-mermaid.spec.ts | Mermaid 历史渲染。 |\n| thread-list-infinite-scroll.spec.ts | 会话列表无限滚动。 |\n| landing.spec.ts | 首页。 |\n| e2e-real-backend | 真实后端契约。 |\n\n```mermaid\nflowchart TD\n  Playwright --> History[thread history]\n  Playwright --> Mermaid[history mermaid]\n  Playwright --> Infinite[thread list infinite scroll]\n  Playwright --> Landing[landing]\n  Playwright --> Real[real backend specs]\n  Real --> Gateway[real Gateway]\n  History --> MockAPI\n  Mermaid --> MockAPI\n  Infinite --> MockAPI\n  Assertions --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "FxBxdvuC4oKStXx2ioBmsLmoyqf",
      "revision_id": 16
    }
  }
}
