{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>133｜Frontend Tests 与 Playwright E2E 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。\n</callout>\n\n---\n\n# 可视化增强：前端测试路径图\n\n<callout emoji=\"💡\">\n**图解目标：**补充前端从组件到 E2E 的测试路径，帮助读者区分 lint/type/unit/e2e。\n</callout>\n\n## 1. Frontend 测试路径图\n\n```mermaid\nflowchart TD\n  UIChange[前端变更] --> Type[TypeScript typecheck]\n  UIChange --> Lint[lint format]\n  UIChange --> Unit[unit tests]\n  UIChange --> E2E[Playwright E2E]\n  Unit --> Components[components hooks]\n  E2E --> Browser[真实浏览器流程]\n  Browser --> Login[auth/setup]\n  Browser --> Chat[chat streaming]\n  Browser --> Artifacts[artifact panel]\n  Type --> CI\n  Lint --> CI\n  Unit --> CI\n  E2E --> CI\n```\n\n| 读图对象 | 图里怎么看 | 维护入口 |\n|-|-|-|\n| 模块职责 | 前端测试覆盖静态检查、组件行为和真实用户流 | frontend tests |\n| 数据流 | 代码变更先过 type/lint，再按风险跑 unit/e2e | pnpm scripts、Playwright |\n| 阅读路径 | 先看 package scripts，再看测试目录和关键 spec | 133 章节 |\n\n| 模块点 | 说明 |\n|-|-|\n| unit tests | core clipboard/reasoning trigger 等单测。 |\n| e2e mock | chat、sidebar、artifact、thread-history 等 mocked backend。 |\n| e2e real backend | auth-disabled、multi-run-order、real-backend-render。 |\n| record tests | record write/read file 流程。 |\n\n```mermaid\nflowchart TD\n  FrontendCode --> Unit[vitest unit]\n  FrontendCode --> E2E[playwright e2e]\n  E2E --> MockBackend[tests e2e mock api]\n  E2E --> RealBackend[e2e real backend]\n  RealBackend --> Gateway[real gateway]\n  Unit --> CI[frontend-unit-tests]\n  E2E --> CI2[e2e-tests]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "OUAUdzRP8oDP2uxkNTbmhpbiyr1",
      "revision_id": 17
    }
  }
}
