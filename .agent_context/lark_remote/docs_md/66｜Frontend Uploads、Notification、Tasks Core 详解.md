<title>66｜Frontend Uploads、Notification、Tasks Core 详解</title>

<callout emoji="✅">
**本章目标：**讲清上传文件、通知、subtask 状态和 prompt input files 的前端数据流。
</callout>

# 1. 模块职责

| 对象 | 说明 |
|-|-|
| `core/uploads/api.ts` | upload/list/delete uploaded files。 |
| `core/uploads/prompt-input-files.ts` | PromptInput file part 转 File。 |
| `core/notification/hooks.ts` | 浏览器通知。 |
| `core/tasks/context.tsx` | SubtasksProvider 状态。 |
| `core/tasks/subtask-result.ts` | 解析 task tool result。 |

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
**设计目的：**前端模块按页面、core hooks、组件拆分，是为了分离路由装配、数据状态和展示组件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是组件复用和状态管理更清晰。 |
| 代价 | 代价是一次交互会跨 React Query、localStorage、useStream 和多个组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components/workspace`。 |
| 阅读路径 | 阅读路径：先找页面入口，再找 hook 数据源，最后看组件如何消费 props/state。 |

```mermaid
flowchart TD
  A[设计动机] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[理解方式]
```