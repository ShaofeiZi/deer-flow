{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>42｜Frontend useThreadStream 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 frontend/src/core/threads/hooks.ts 如何封装 LangGraph useStream、提交消息、处理历史和缓存。\n</callout>\n\n| 区域 | 职责 |\n|-|-|\n| `useThreadStream` | 核心 streaming hook，封装 useStream callbacks。 |\n| `sendMessage` | 乐观 UI、文件上传、thread.submit。 |\n| `mergeMessages` | 合并 optimistic/history/stream messages。 |\n| `useThreadHistory` | 分页读取历史 run messages。 |\n| `useInfiniteThreads` | 会话列表无限滚动。 |\n| `useDeleteThread/useRenameThread` | 线程删除和重命名。 |\n\n```mermaid\nflowchart TD\n  ChatPage --> Hook[useThreadStream]\n  Hook --> UseStream[LangGraph useStream]\n  Hook --> Send[sendMessage]\n  Send --> Optimistic[optimistic messages]\n  Send --> Upload[upload files]\n  Send --> Submit[thread.submit]\n  UseStream --> Created[onCreated]\n  UseStream --> Update[onUpdateEvent]\n  UseStream --> Custom[onCustomEvent]\n  UseStream --> Finish[onFinish]\n  Update --> Cache[React Query cache updates]\n  Finish --> Invalidate[invalidate thread/token caches]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "FAKHdFdrxoDN17x6L2pmRh8LyLh",
      "revision_id": 17
    }
  }
}
