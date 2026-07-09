<title>285｜Frontend Core Todos / Tasks / Tools 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 channels/auth/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| core/todos | Todo 类型。 |
| core/tasks/context.tsx | SubtasksProvider。 |
| core/tasks/subtask-result.ts | 解析 subtask result。 |
| core/tools/utils.ts | tool call 工具辅助。 |

```mermaid
flowchart TD
  ThreadValues --> TodosTypes
  TaskToolCall --> SubtasksProvider
  ToolResult --> ParseSubtaskResult
  ParseSubtaskResult --> SubtasksProvider
  SubtasksProvider --> SubtaskCard
  ToolCalls --> ToolUtils
  ToolUtils --> MessageGroup
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
sequenceDiagram
  participant Stream as threads/hooks useStream
  participant List as message-list render
  participant Ctx as SubtasksProvider context
  participant Parser as parseSubtaskResult
  participant Card as SubtaskCard
  participant ToolExp as explainLastToolCall
  Stream->>List: assistant subagent message group
  List->>List: match tool_calls name task
  List->>Ctx: updateSubtask status in_progress
  Ctx->>Card: useSubtask id returns in_progress
  Card->>ToolExp: explainLastToolCall latestMessage
  ToolExp-->>Card: tool call label
  Stream->>List: tool result ToolMessage
  List->>Parser: text plus additional_kwargs
  alt subagent_status stamp present
    Parser->>Parser: readStructuredStatus maps enum
  else no stamp
    Parser->>Parser: parseFromText prefix match
  end
  Parser-->>List: SubtaskResultUpdate status result error
  List->>Ctx: updateSubtask merge parsed update
  Ctx->>Card: status completed or failed
  Card->>Card: render status pill
```