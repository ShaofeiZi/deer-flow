<title>51｜thread_runs.py Router 单文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲清 thread_runs.py 的接口职责、数据流和修改风险。
</callout>

# 1. 接口职责

| 接口 | 职责 |
|-|-|
| `POST /{thread_id}/runs` | 创建后台 run。 |
| `POST /{thread_id}/runs/stream` | 创建 run 并 SSE stream。 |
| `POST /{thread_id}/runs/wait` | 同步等待 run 完成。 |
| `POST /{thread_id}/runs/{run_id}/cancel` | 取消或 rollback。 |
| `GET messages/events/token-usage` | 读取 run/thread 事件和用量。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  Request[RunCreateRequest] --> Authz[require_permission runs create]
  Authz --> Start[start_run]
  Start --> Record[RunRecord]
  Record --> Stream{stream or wait?}
  Stream -->|stream| SSE[StreamingResponse sse_consumer]
  Stream -->|wait| Final[wait_for_run_completion]
  Record --> RunStore[RunManager store]
  Cancel[cancel request] --> RunManager[RunManager cancel]
```

# 3. 修改建议

- 先改 Pydantic request/response，再改 handler。
- 涉及用户数据必须确认 owner check 或 current user。
- 前端调用方要同步更新 core API/hook。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |
| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |
| 重点代码 | 标题对应的源码、测试或文档入口。 |
| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |

```mermaid
stateDiagram-v2
  [*] --> pending : RunManager.create_or_reject
  pending --> running : worker.run_agent set_status
  pending --> interrupted : RunManager.cancel interrupt
  running --> success : worker normal completion
  running --> error : exception or llm_error_fallback
  running --> error : cancel rollback
  running --> interrupted : cancel interrupt
  success --> [*]
  error --> [*]
  interrupted --> [*]
```
