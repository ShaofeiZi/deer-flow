{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 256｜Frontend Build/Test Configs 详解\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| next.config.js | Next.js 配置。 |\n| tsconfig.json | TS 编译配置。 |\n| eslint.config.js | Lint 配置。 |\n| vitest.config.ts | 单测配置。 |\n| playwright.config.ts | E2E 配置。 |\n| pnpm-workspace.yaml | workspace。 |\n\n```mermaid\nflowchart TD\n  Source --> Typecheck[tsconfig]\n  Source --> Lint[eslint]\n  Source --> Unit[vitest]\n  Source --> E2E[playwright]\n  Source --> NextBuild[next config]\n  PNPM[pnpm workspace] --> Install\n  Typecheck --> CI\n  Lint --> CI\n  Unit --> CI\n  E2E --> CI\n  NextBuild --> Deploy\n```",
      "document_id": "I76gdhKYMoyRZJxJZ40m2U8Cyid",
      "revision_id": 18
    }
  }
}
