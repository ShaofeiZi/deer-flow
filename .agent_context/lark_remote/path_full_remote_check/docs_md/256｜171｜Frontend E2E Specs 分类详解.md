{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>171｜Frontend E2E Specs 分类详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/CI/脚本模块，说明覆盖范围、运行入口和逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| chat.spec / agent-chat | 聊天主流程。 |\n| sidebar / thread-list | 侧边栏和会话列表。 |\n| artifact-preview | artifact 面板。 |\n| thread-history / mermaid | 历史消息和 mermaid 渲染。 |\n| real-backend specs | 真实后端渲染和多 run 顺序。 |\n\n```mermaid\nflowchart TD\n  Playwright --> MockE2E[frontend tests e2e]\n  Playwright --> RealE2E[e2e real backend]\n  MockE2E --> MockAPI[mock-api]\n  MockAPI --> Browser[UI assertions]\n  RealE2E --> Gateway[real Gateway]\n  Gateway --> Browser\n  Browser --> CI[e2e workflows]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "UdJLd1PnjoCoaRxPymZmxYwAymg",
      "revision_id": 16
    }
  }
}
