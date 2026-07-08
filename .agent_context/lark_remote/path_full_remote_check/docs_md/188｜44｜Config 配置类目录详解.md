{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>44｜Config 配置类目录详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**把 config 包中各配置类按领域归类，说明它们如何进入 AppConfig 和运行时。\n</callout>\n\n| 配置类/文件 | 职责 |\n|-|-|\n| `model_config.py` | 模型 provider、API 参数、thinking/vision 能力声明。 |\n| `sandbox_config.py` | sandbox provider、mounts、allow_host_bash。 |\n| `subagents_config.py` | 内置/自定义 subagent override。 |\n| `summarization_config.py` | 摘要触发、保留策略、summary prompt。 |\n| `tool_output_config.py` | 工具输出预算阈值。 |\n| `tool_search_config.py` | deferred tool search 开关。 |\n| `tracing_config.py` | LangSmith/Langfuse tracing。 |\n| `run_events_config.py` | run events 存储配置。 |\n\n```mermaid\nflowchart TD\n  ConfigYaml[config yaml] --> AppConfig[AppConfig]\n  AppConfig --> Model[ModelConfig]\n  AppConfig --> Sandbox[SandboxConfig]\n  AppConfig --> Memory[MemoryConfig]\n  AppConfig --> Subagents[SubagentsAppConfig]\n  AppConfig --> Summary[SummarizationConfig]\n  AppConfig --> Tools[ToolConfig and ToolOutputConfig]\n  AppConfig --> Tracing[TracingConfig]\n  AppConfig --> Runtime[Gateway and lead_agent runtime]\n  Runtime --> Middleware[Middleware factories]\n  Runtime --> Providers[model sandbox store providers]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是查找和学习更快，职责更聚焦。 |\n| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |\n| 重点代码 | 重点代码见本章表格列出的源码路径。 |\n| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "KkxxdGMdMoQL7xxJ68KmYRXNy5d",
      "revision_id": 15
    }
  }
}
