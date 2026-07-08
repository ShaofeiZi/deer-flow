{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>134｜GitHub Workflows CI 流水线详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| backend-unit-tests.yml | 后端 pytest。 |\n| frontend-unit-tests.yml | 前端单测/类型。 |\n| e2e-tests.yml | Playwright E2E。 |\n| replay-e2e.yml | Replay 契约。 |\n| backend-blocking-io-tests.yml | 阻塞 IO gate。 |\n| lint-check.yml | lint 检查。 |\n| container.yaml | 容器构建。 |\n\n```mermaid\nflowchart TD\n  Push[push or PR] --> Backend[backend unit tests]\n  Push --> Frontend[frontend unit tests]\n  Push --> E2E[e2e tests]\n  Push --> Replay[replay e2e]\n  Push --> Blocking[blocking io tests]\n  Push --> Lint[lint check]\n  Push --> Container[container build]\n  Results --> PRStatus[PR checks]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "AuwvdIOcHocJNfxTv36mx07PyOb",
      "revision_id": 16
    }
  }
}
