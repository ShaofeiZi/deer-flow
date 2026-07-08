{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 267｜runtime/runs/naming.py 与 schemas.py 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| naming.py | resolve_root_run_name。 |\n| schemas.py | RunStatus、DisconnectMode。 |\n| run_name | tracing/journal 中用于识别 root run。 |\n| status enum | `pending`、`running`、`success`、`error`、`timeout`、`interrupted`。注意没有 `cancelled`，取消后 run 状态是 `interrupted`。 |\n| disconnect enum | `cancel`、`continue` 是 SSE 断开后的处理策略，不是 RunStatus。 |\n\n```mermaid\nflowchart TD\n  AssistantId --> Naming[resolve root run name]\n  Config --> Naming\n  Naming --> RunnableConfig\n  Schemas --> RunStatus\n  Schemas --> DisconnectMode\n  RunStatus --> RunRecord\n  DisconnectMode --> DisconnectPolicy[disconnect policy]\n  DisconnectPolicy --> start_run\n  RunnableConfig --> Tracing\n```",
      "document_id": "XSF2dZOJCohf2UxB01CmoF4xyFs",
      "revision_id": 20
    }
  }
}
