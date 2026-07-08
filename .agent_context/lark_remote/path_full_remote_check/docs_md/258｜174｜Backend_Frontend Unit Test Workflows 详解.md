{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>174｜Backend/Frontend Unit Test Workflows 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| backend-unit-tests.yml | 安装后端依赖并运行 pytest。 |\n| frontend-unit-tests.yml | 安装前端依赖并运行 unit/type/lint。 |\n| lint-check.yml | 统一 lint 检查。 |\n| 触发 | PR/push 触发质量 gate。 |\n\n```mermaid\nflowchart TD\n  PR[PR or push] --> BackendWF[backend unit tests]\n  PR --> FrontendWF[frontend unit tests]\n  PR --> Lint[lint check]\n  BackendWF --> UV[uv sync]\n  UV --> Pytest[pytest]\n  FrontendWF --> PNPM[pnpm install]\n  PNPM --> Vitest[vitest/typecheck]\n  Pytest --> Status[GitHub check]\n  Vitest --> Status\n  Lint --> Status\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Mi1IdEdyNoRM9exWg0HmwvLwy9d",
      "revision_id": 16
    }
  }
}
