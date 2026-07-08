{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>43｜Frontend Message Utils 与 Artifacts Hooks 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清消息分组、reasoning/content 提取、artifact 内容加载和 URL 构造。\n</callout>\n\n| 文件 | 职责 |\n|-|-|\n| `frontend/src/core/messages/utils.ts` | getMessageGroups、reasoning 提取、hidden message 过滤、uploaded files 解析。 |\n| `components/workspace/messages/message-list.tsx` | 按 MessageGroup 渲染普通消息、processing、subagent、present files。 |\n| `frontend/src/core/artifacts/utils.ts` | 构造 artifact URL、判断文件类型。 |\n| `frontend/src/core/artifacts/hooks.ts` | useArtifactContent 拉取 artifact 内容。 |\n| `components/workspace/artifacts/*` | 列表、详情、触发器、预览和安装 .skill。 |\n\n```mermaid\nflowchart TD\n  Messages[thread.messages] --> Groups[getMessageGroups]\n  Groups --> Human[human]\n  Groups --> Assistant[assistant]\n  Groups --> Processing[processing]\n  Groups --> Present[present files]\n  Groups --> Subagent[subagent]\n  Present --> ArtifactList[ArtifactFileList]\n  State[thread.values.artifacts] --> Provider[ArtifactsProvider]\n  Provider --> Detail[ArtifactFileDetail]\n  Detail --> Hook[useArtifactContent]\n  Hook --> API[GET artifact URL]\n  API --> Preview[CodeEditor or iframe or download]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是查找和学习更快，职责更聚焦。 |\n| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |\n| 重点代码 | 重点代码见本章表格列出的源码路径。 |\n| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "LKNFdYQDFob1Pnxz0nTmHIRDy5b",
      "revision_id": 17
    }
  }
}
