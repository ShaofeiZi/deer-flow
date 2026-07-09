<title>66｜Frontend Uploads、Notification、Tasks Core 详解</title>

<callout emoji="✅">
**本章目标：**讲清上传文件、通知、subtask 状态和 prompt input files 的前端数据流。
</callout>

# 1. 模块职责

| 对象 | 说明 |
|-|-|
| `frontend/src/core/uploads/api.ts` | upload/list/delete uploaded files。 |
| `frontend/src/core/uploads/prompt-input-files.ts` | PromptInput file part 转 File。 |
| `frontend/src/core/notification/hooks.ts` | 浏览器通知。 |
| `frontend/src/core/tasks/context.tsx` | SubtasksProvider 状态。 |
| `frontend/src/core/tasks/subtask-result.ts` | 解析 task tool result。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  InputBox --> FileParts[prompt input files]
  FileParts --> UploadAPI[uploadFiles]
  UploadAPI --> Gateway[uploads router]
  Stream[custom events] --> Tasks[SubtasksProvider]
  ToolResult[task tool result] --> Parse[parseSubtaskResult]
  Parse --> Tasks
  Finish[onFinish] --> Notify[useNotification]
  Notify --> Browser[Browser notification]
```

# 3. 排障与修改建议

- 先确认调用方和数据源，再改 schema。
- 涉及用户数据必须确认鉴权和 owner check。
- 涉及缓存需要同步 invalidate 或 reset。

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
flowchart TD
  TM[ToolMessage content] --> Parse[parseSubtaskResult]
  Parse --> Struct[readStructuredStatus]
  Struct --> Has{subagent_status stamped}
  Has -->|no| FromText[parseFromText]
  Has -->|yes| Map[STRUCTURED_STATUS_TO_SUBTASK]
  Map --> Mapped[mapped to completed or failed]
  FromText --> Prefix{prefix match}
  Prefix -->|SUCCESS_PREFIX| Completed[completed]
  Prefix -->|FAILURE/TIMEOUT/CANCELLED/ERROR| Failed[failed]
  Prefix -->|no match| InProg[in_progress]
  Mapped --> Update[useUpdateSubtask]
  Completed --> Update
  Failed --> Update
  InProg --> Update
  Update --> Card[Subtask card pill]
```
