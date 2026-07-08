{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>193｜Tracing / Token Usage Tests 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 Docker、Provisioner、脚本和测试细模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| test_tracing_config/factory/metadata | tracing 配置、回调、metadata。 |\n| test_token_usage.py | token usage 聚合。 |\n| test_token_usage_middleware.py | middleware attribution。 |\n| test_thread_token_usage.py | thread 级 token usage API。 |\n| test_task_tool_usage_recorder.py | task tool 用量记录。 |\n\n```mermaid\nflowchart TD\n  LLMCall --> TokenUsageMW\n  TokenUsageMW --> UsageRecords\n  UsageRecords --> TokenTests\n  RunConfig --> TracingConfig\n  TracingConfig --> TracingFactory\n  TracingFactory --> TraceMetadata\n  TraceMetadata --> TracingTests\n  TokenTests --> CI\n  TracingTests --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "QXKRdL3tUoqa5LxPRPwm1OgNyqj",
      "revision_id": 16
    }
  }
}
