{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>25｜UploadsMiddleware 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清上传文件如何被转换为 agent 可读上下文。\n</callout>\n\n| 函数 | 职责 |\n|-|-|\n| `_files_from_kwargs` | 从 HumanMessage additional_kwargs.files 提取新上传文件。 |\n| `_extract_outline_for_file` | 读取转换出的同名 .md，提取标题 outline 或首几行预览。 |\n| `_create_files_message` | 生成 `<uploaded_files>` 上下文块。 |\n| `before_agent` | 合并新文件和历史文件，替换最后一条 human message。 |\n\n```mermaid\nflowchart TD\n  A[HumanMessage additional_kwargs.files] --> B[validate filename]\n  B --> C[check uploads directory]\n  C --> D[collect new files]\n  E[scan historical uploads] --> F[exclude new files]\n  D --> G[extract outline from converted markdown]\n  F --> G\n  G --> H[build uploaded_files block]\n  H --> I[prepend to last HumanMessage]\n  I --> J[return uploaded_files and messages]\n```\n\n排障重点：如果模型不知道文件，先确认前端 uploadFiles 返回的 files 是否进入 additional_kwargs，再确认 uploads 目录里是否存在真实文件和转换后的 Markdown。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |\n| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |\n| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |\n| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "IiQ9dfvfUoPcXLxr8JTmgS5nyKb",
      "revision_id": 15
    }
  }
}
