{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>338｜Frontend package/Docker/Makefile 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 remaining scripts/tests/routes/package docs 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| frontend/package.json | scripts/dependencies。 |\n| frontend/Makefile | 前端命令封装。 |\n| frontend/Dockerfile | 前端镜像。 |\n| pnpm-lock.yaml | 依赖锁。 |\n| next.config.js | Next 配置。 |\n\n```mermaid\nflowchart TD\n  PackageJson --> PNPMInstall\n  PackageJson --> Scripts\n  Scripts --> Dev\n  Scripts --> Build\n  Scripts --> Test\n  Dockerfile --> FrontendImage\n  NextConfig --> Build\n  PnpmLock --> PNPMInstall\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "VJW6d2Ux5oDWoLxkQuDmn6k6yMh",
      "revision_id": 16
    }
  }
}
