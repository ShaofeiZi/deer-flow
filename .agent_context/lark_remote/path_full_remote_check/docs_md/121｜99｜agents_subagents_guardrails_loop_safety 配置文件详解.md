{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>99｜agents/subagents/guardrails/loop/safety 配置文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| agents_config | custom agent config/SOUL 路径解析。 |\n| subagents_config | subagent override/custom subagent。 |\n| guardrails_config | guardrail provider。 |\n| loop_detection_config | 循环检测阈值。 |\n| safety_finish_reason_config | 安全终止 detector 配置。 |\n\n```mermaid\nflowchart TD\n  ConfigYaml --> AgentsConfig\n  ConfigYaml --> SubagentsConfig\n  ConfigYaml --> GuardrailsConfig\n  ConfigYaml --> LoopConfig\n  ConfigYaml --> SafetyConfig\n  AgentsConfig --> LeadAgent\n  SubagentsConfig --> SubagentRegistry\n  GuardrailsConfig --> GuardrailMiddleware\n  LoopConfig --> LoopDetectionMiddleware\n  SafetyConfig --> SafetyFinishReasonMiddleware\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这些配置文件控制 agent 身份、subagent 覆盖、工具调用授权、循环保护和安全终止处理，是运行时行为边界而不是前端展示层。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | custom agent、subagent、guardrail、loop detection 和 safety detector 可以独立配置和测试。 |\n| 代价 | agent 配置存在 per-user 与 legacy fallback；`skills: None`、`skills: []`、指定列表含义不同，误配会直接改变 prompt 能力注入。 |\n| 重点代码 | `agents_config.py`、`subagents_config.py`、`guardrails_config.py`、`loop_detection_config.py`、`safety_finish_reason_config.py`。 |\n| 阅读路径 | 先看配置字段默认值，再追踪到 lead agent/subagent registry/middleware，最后用 run 行为验证 tool allow/deny、loop warning/hard stop、安全 tool-call suppression。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "U1EAd9aqMoIVTrxNoqkmNyJyy0b",
      "revision_id": 18
    }
  }
}
