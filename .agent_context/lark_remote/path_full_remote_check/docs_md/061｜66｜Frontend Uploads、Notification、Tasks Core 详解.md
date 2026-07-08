{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>66｜Frontend Uploads、Notification、Tasks Core 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清上传文件、通知、subtask 状态和 prompt input files 的前端数据流。\n</callout>\n\n# 1. 模块职责\n\n| 对象 | 说明 |\n|-|-|\n| `frontend/src/core/uploads/api.ts` | upload/list/delete uploaded files。 |\n| `frontend/src/core/uploads/prompt-input-files.ts` | PromptInput file part 转 File。 |\n| `frontend/src/core/notification/hooks.ts` | 浏览器通知。 |\n| `frontend/src/core/tasks/context.tsx` | SubtasksProvider 状态。 |\n| `frontend/src/core/tasks/subtask-result.ts` | 解析 task tool result。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  InputBox --> FileParts[prompt input files]\n  FileParts --> UploadAPI[uploadFiles]\n  UploadAPI --> Gateway[uploads router]\n  Stream[custom events] --> Tasks[SubtasksProvider]\n  ToolResult[task tool result] --> Parse[parseSubtaskResult]\n  Parse --> Tasks\n  Finish[onFinish] --> Notify[useNotification]\n  Notify --> Browser[Browser notification]\n```\n\n# 3. 排障与修改建议\n\n- 先确认调用方和数据源，再改 schema。\n- 涉及用户数据必须确认鉴权和 owner check。\n- 涉及缓存需要同步 invalidate 或 reset。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "IdEZdZcDeoADdIxMfjWmETbEyLb",
      "revision_id": 19
    }
  }
}
