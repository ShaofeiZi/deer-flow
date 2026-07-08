{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>172｜GitHub Workflow 文件逐项详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/CI/脚本模块，说明覆盖范围、运行入口和逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| backend-unit-tests.yml | 运行后端测试。 |\n| frontend-unit-tests.yml | 运行前端单测/类型。 |\n| e2e-tests.yml | Playwright E2E。 |\n| replay-e2e.yml | Replay golden。 |\n| backend-blocking-io-tests.yml | 阻塞 IO gate。 |\n| container.yaml | 容器构建。 |\n| label-sync/triage | 项目维护自动化。 |\n\n```mermaid\nflowchart TD\n  PR[Pull Request] --> Backend[backend unit tests]\n  PR --> Frontend[frontend unit tests]\n  PR --> E2E[e2e tests]\n  PR --> Replay[replay e2e]\n  PR --> Blocking[blocking io]\n  PR --> Lint[lint check]\n  PR --> Container[container build]\n  Maint[scheduled/manual] --> Labels[label sync]\n  Maint --> Triage[triage]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是文档/脚本容易随代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "PB7GdUM7CozMjaxHX12ms1SHyYK",
      "revision_id": 15
    }
  }
}
