{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>198｜Frontend Unit 与 Real Backend Tests 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续补齐剩余测试与文档规格模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| unit/core/clipboard.test.ts | 剪贴板单测。 |\n| unit/core/reasoning-trigger.test.ts | reasoning 触发单测。 |\n| e2e-real-backend/auth-disabled-contract | 真实后端 auth disabled 合同。 |\n| e2e-real-backend/multi-run-order | 多 run 顺序。 |\n| e2e-real-backend/real-backend-render | 真实后端渲染。 |\n\n```mermaid\nflowchart TD\n  FrontendCore --> UnitTests\n  UnitTests --> Clipboard\n  UnitTests --> ReasoningTrigger\n  RealBackend --> AuthContract\n  RealBackend --> MultiRunOrder\n  RealBackend --> Render\n  AuthContract --> Gateway\n  MultiRunOrder --> Gateway\n  Render --> BrowserAssertions\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "OM24d78EKoUa3rx7BW4mFipayec",
      "revision_id": 16
    }
  }
}
