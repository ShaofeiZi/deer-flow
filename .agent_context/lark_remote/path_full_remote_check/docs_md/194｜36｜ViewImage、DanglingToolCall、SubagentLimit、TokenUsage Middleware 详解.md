{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>36｜ViewImage、DanglingToolCall、SubagentLimit、TokenUsage Middleware 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐剩余辅助 middleware：视觉上下文、悬空 tool call 修复、子代理并发限制、token usage 归因。\n</callout>\n\n| Middleware | 职责 | 运行点 |\n|-|-|-|\n| ViewImageMiddleware | view_image 工具完成后，把图片详情注入为视觉模型可读 HumanMessage。 | before_model |\n| DanglingToolCallMiddleware | 历史中 AI tool_call 缺 ToolMessage 时补 synthetic ToolMessage。 | wrap_model_call |\n| SubagentLimitMiddleware | 同轮 task tool_calls 超过上限时截断。 | after_model |\n| TokenUsageMiddleware | 记录 token usage、todo action、tool attribution。 | model/tool hooks |\n\n```mermaid\nflowchart TD\n  History[message history] --> Dangling[DanglingToolCall patches missing ToolMessages]\n  Dangling --> Model[model call]\n  Model --> SubLimit[SubagentLimit truncates extra task calls]\n  Model --> Token[TokenUsage attribution]\n  Tool[view_image tool result] --> Viewed[viewed_images state]\n  Viewed --> ViewImage[ViewImageMiddleware injects image details]\n  ViewImage --> NextModel[next model call sees images]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是查找和学习更快，职责更聚焦。 |\n| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |\n| 重点代码 | 重点代码见本章表格列出的源码路径。 |\n| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "FGBSd60wYoPStFxTn1wmos4Iyhd",
      "revision_id": 15
    }
  }
}
