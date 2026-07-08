<title>266｜runtime/runs/manager.py 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 runtime、subagents、tools builtins 单文件模块。
</callout>

## 本轮源码校准补充：RunManager 状态机

| 功能 | 说明 |
|-|-|
| create/reject | 默认并发策略是 reject，已有 active run 时返回冲突。 |
| interrupt/rollback | 可按策略中断或回滚已有 run，但 `enqueue` 当前不支持。 |
| store | 可接 RunRepository 或 MemoryRunStore，决定 run 历史是否持久化。 |
| reconcile | 启动时可恢复/清理 orphan running runs，避免服务重启后状态悬挂。 |

| 模块点 | 说明 |
|-|-|
| RunRecord | run 元数据和状态。 |
| RunManager | 创建/查询/取消 run。 |
| ConflictError | 并发策略冲突。 |
| reconcile | 启动时恢复 orphan running runs。 |
| store | 可用 RunRepository 或 MemoryRunStore。 |

```mermaid
flowchart TD
  Router --> RunManager
  RunManager --> Create[create_or_reject]
  Create --> RunRecord
  RunRecord --> Store[RunStore]
  Cancel --> RunManager
  RunManager --> Status[set_status]
  Startup --> Reconcile[reconcile orphan inflight]
  Reconcile --> Store
```


```mermaid
stateDiagram-v2
  [*] --> pending: create_or_reject
  pending --> running: worker set_status
  running --> success: graph stream completes
  running --> error: exception or LLM fallback
  running --> interrupted: cancel or interrupt
  pending --> interrupted: cancel before worker starts
  pending --> error: startup orphan reconcile
  running --> error: startup orphan reconcile
  running --> error: rollback requested and checkpoint restore attempted
  success --> [*]
  error --> [*]
  interrupted --> [*]
```
