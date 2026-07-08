{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>236｜backend/docs/summarization.md 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化 content/spec/docs 单模块，补充运行/维护逻辑图。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| summarization.md | 摘要机制说明。 |\n| SummarizationMiddleware | 实现。 |\n| memory_flush_hook | 摘要前 flush memory。 |\n| skill preserve | 保留近期 skill 上下文。 |\n\n```mermaid\nflowchart TD\n  ContextTooLong --> SummarizationMiddleware\n  SummarizationMiddleware --> FlushMemory\n  SummarizationMiddleware --> SelectMessages\n  SelectMessages --> PreserveSkills\n  SelectMessages --> LLM[summary model]\n  LLM --> SummaryMessage\n  SummaryMessage --> NewContext\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**summarization 在模型调用前压缩旧消息，同时保留最近上下文、AI/Tool 配对、memory flush 机会和最近 skill 读取结果。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 长对话不容易超过上下文窗口，并能在压缩前把重要记忆和 skill 指令尽量保留下来。 |\n| 代价 | 压缩会改变 checkpoint 中的 messages；如果 history 只读 checkpoint，可能丢失被压缩的原始消息。 |\n| 重点代码 | `backend/docs/summarization.md`、`deerflow/agents/middlewares/summarization_middleware.py`、`deerflow/agents/memory/summarization_hook.py`、`deerflow/config/summarization_config.py`。 |\n| 阅读路径 | 先读 config 的 trigger/keep/skill rescue，再看 middleware 如何 partition messages，最后看 RunEventStore/history 是否补足可见历史。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```\n\n```mermaid\nflowchart TD\n  BeforeModel --> TriggerCheck[trigger threshold]\n  TriggerCheck --> Partition[older vs preserved messages]\n  Partition --> MemoryFlush[memory flush hook]\n  Partition --> SkillRescue[preserve recent skill reads]\n  SkillRescue --> SummaryLLM[summary model]\n  SummaryLLM --> SummaryMessage[summary message]\n  SummaryMessage --> CheckpointMessages[compressed checkpoint messages]\n  RunJournal --> EventStore[original display history]\n```",
      "document_id": "JmG0dE4vkoeARLxZWRxmucbByTg",
      "revision_id": 18
    }
  }
}
