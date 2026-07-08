{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 266｜runtime/runs/manager.py 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。\n</callout>\n\n## 本轮源码校准补充：RunManager 状态机\n\n| 功能 | 说明 |\n|-|-|\n| create/reject | 默认并发策略是 reject，已有 active run 时返回冲突。 |\n| interrupt/rollback | 可按策略中断或回滚已有 run，但 `enqueue` 当前不支持。 |\n| store | 可接 RunRepository 或 MemoryRunStore，决定 run 历史是否持久化。 |\n| reconcile | 启动时可恢复/清理 orphan running runs，避免服务重启后状态悬挂。 |\n\n| 模块点 | 说明 |\n|-|-|\n| RunRecord | run 元数据和状态。 |\n| RunManager | 创建/查询/取消 run。 |\n| ConflictError | 并发策略冲突。 |\n| reconcile | 启动时恢复 orphan running runs。 |\n| store | 可用 RunRepository 或 MemoryRunStore。 |\n\n```mermaid\nflowchart TD\n  Router --> RunManager\n  RunManager --> Create[create_or_reject]\n  Create --> RunRecord\n  RunRecord --> Store[RunStore]\n  Cancel --> RunManager\n  RunManager --> Status[set_status]\n  Startup --> Reconcile[reconcile orphan inflight]\n  Reconcile --> Store\n```\n\n```mermaid\nstateDiagram-v2\n  [*] --> pending: create_or_reject\n  pending --> running: worker set_status\n  running --> success: graph stream completes\n  running --> error: exception or LLM fallback\n  running --> interrupted: cancel or interrupt\n  pending --> interrupted: cancel before worker starts\n  pending --> error: startup orphan reconcile\n  running --> error: startup orphan reconcile\n  running --> error: rollback requested and checkpoint restore attempted\n  success --> [*]\n  error --> [*]\n  interrupted --> [*]\n```",
      "document_id": "CEyzdci8noYLpux4gzVmCKUiyvf",
      "revision_id": 22
    }
  }
}
