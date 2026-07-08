{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>132｜Backend Tests 测试体系详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。\n</callout>\n\n---\n\n# 可视化增强：后端测试金字塔\n\n<callout emoji=\"💡\">\n**图解目标：**补充后端测试层级和运行入口，便于读者从变更类型选择测试。\n</callout>\n\n## 1. Backend 测试选择图\n\n```mermaid\nflowchart TD\n  Change[后端变更] --> ConfigChange[配置变更]\n  Change --> RuntimeChange[运行时变更]\n  Change --> RouterChange[API router 变更]\n  Change --> ToolChange[工具或 sandbox 变更]\n  ConfigChange --> Unit[unit tests]\n  RuntimeChange --> Integration[integration tests]\n  RouterChange --> HTTP[HTTP e2e]\n  ToolChange --> SandboxTests[sandbox/tool tests]\n  Unit --> CI[CI]\n  Integration --> CI\n  HTTP --> CI\n  SandboxTests --> CI\n```\n\n| 读图对象 | 图里怎么看 | 维护入口 |\n|-|-|-|\n| 模块职责 | 把测试按变更类型分层 | backend/tests |\n| 数据流 | 变更类型决定最小测试集，再进入 CI | pytest、Makefile、GitHub workflows |\n| 阅读路径 | 先定位变更域，再选 unit/integration/e2e | 132 章节 |\n\n| 模块点 | 说明 |\n|-|-|\n| unit tests | 覆盖 config、runtime、middlewares、routers、tools、memory、MCP、sandbox 等。 |\n| blocking_io tests | 检查异步路径不阻塞 event loop。 |\n| replay tests | 用 golden fixture 验证 SSE/渲染契约。 |\n| e2e/helpers | 真实 gateway/client 辅助测试。 |\n\n```mermaid\nflowchart TD\n  BackendCode --> UnitTests[backend/tests]\n  BackendCode --> Blocking[tests/blocking_io]\n  Runtime --> Replay[test_replay_golden]\n  Client --> ClientE2E[test_client_e2e]\n  Pytest[uv run pytest] --> UnitTests\n  Pytest --> Blocking\n  CI[GitHub Actions] --> Pytest\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "XnvOdeyO4ofXDPxGUwqmobtdyte",
      "revision_id": 17
    }
  }
}
