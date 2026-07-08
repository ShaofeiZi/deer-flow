{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 265｜runtime/runs/worker.py 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。\n</callout>\n\n## 本轮源码校准补充：run_agent worker\n\n```mermaid\nflowchart TD\n  Start[run_agent] --> Status[set running]\n  Status --> Metadata[publish metadata]\n  Metadata --> Runtime[build Runtime context]\n  Runtime --> Agent[agent_factory -> graph]\n  Agent --> Astream[agent.astream]\n  Astream --> Publish[publish events to StreamBridge]\n  Publish --> Complete[status/title/journal cleanup]\n```\n\n| 步骤 | 说明 |\n|-|-|\n| runtime context | 总是包含 `thread_id`、`run_id`，并合并 caller context 和 app_config。 |\n| stream mode | `events` 目前不通过 Gateway 支持；values/messages/custom 等会被映射。 |\n| rollback | 运行前会尽力捕获 checkpoint，便于 rollback 策略恢复。 |\n| cleanup | 完成后 flush journal、更新状态/标题，并调度 stream bridge cleanup。 |\n\n| 模块点 | 说明 |\n|-|-|\n| run_agent | 后台执行 agent graph。 |\n| Runtime context | 注入 run_id/thread_id/store/checkpointer。 |\n| astream | 消费 LangGraph stream chunks。 |\n| rollback | 支持 pre-run checkpoint rollback。 |\n| finalize | flush journal、更新 run/thread status、publish_end。 |\n\n```mermaid\nsequenceDiagram\n  participant S as start_run\n  participant W as run_agent\n  participant A as agent_factory\n  participant G as graph astream\n  participant B as StreamBridge\n  S->>W: create task\n  W->>A: make lead agent\n  A-->>W: graph\n  W->>G: astream\n  G-->>W: chunks\n  W->>B: publish events\n  W->>W: finalize status journal title\n  W->>B: publish end\n```",
      "document_id": "RiDUdoENFo47jfxIXErmMtTryxb",
      "revision_id": 20
    }
  }
}
