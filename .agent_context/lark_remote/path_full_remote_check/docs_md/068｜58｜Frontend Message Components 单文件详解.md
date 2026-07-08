{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>58｜Frontend Message Components 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清 Message components 的接口职责、数据流和修改风险。\n</callout>\n\n# 1. 接口职责\n\n| 组件 | 职责 |\n|-|-|\n| `message-list.tsx` | 总体消息列表、历史加载、分组渲染。 |\n| `message-list-item.tsx` | 单条 human/assistant 消息展示。 |\n| `message-group.tsx` | reasoning/tool call 过程展示。 |\n| `subtask-card.tsx` | task/subagent 状态卡片。 |\n| `markdown-content.tsx` | Markdown 渲染。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Thread[thread.messages] --> List[MessageList]\n  List --> Groups[getMessageGroups]\n  Groups --> Item[MessageListItem]\n  Groups --> Group[MessageGroup]\n  Groups --> Subtask[SubtaskCard]\n  Groups --> Artifact[ArtifactFileList]\n  Groups --> Clarify[MarkdownContent]\n  List --> History[load more history sentinel]\n```\n\n# 3. 修改建议\n\n- 先改 Pydantic request/response，再改 handler。\n- 涉及用户数据必须确认 owner check 或 current user。\n- 前端调用方要同步更新 core API/hook。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Pj9cdb03Ro5PKWxWuPOmQCk9ysd",
      "revision_id": 17
    }
  }
}
