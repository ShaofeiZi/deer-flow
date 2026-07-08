{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 130｜Core Threads Stream、History、Cache 函数组详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| useThreadStream | 封装 useStream 和 sendMessage。 |\n| mergeMessages | 合并 optimistic/history/stream messages。 |\n| useThreadHistory | 读取历史 run messages。 |\n| upsertThreadInSearchCache | 更新 thread 搜索缓存。 |\n| useInfiniteThreads | 会话列表分页。 |\n\n```mermaid\nflowchart TD\n  ChatPage --> useThreadStream\n  useThreadStream --> useThreadHistory[load historical run messages]\n  useThreadStream --> useStream[LangGraph useStream]\n  UserSubmit --> sendMessage\n  sendMessage --> Baseline[pending usage baseline]\n  sendMessage --> Optimistic{hide_from_ui?}\n  Optimistic -->|no| HumanOptimistic[optimistic human message]\n  Optimistic -->|yes| NoOptimistic[skip visible optimistic row]\n  sendMessage --> Uploads{files?}\n  Uploads -->|yes| UploadFiles[convert + upload files]\n  UploadFiles --> UploadedKwargs[additional_kwargs.files uploaded]\n  Uploads -->|no| Submit\n  UploadedKwargs --> Submit\n  Submit --> ContextFlags[thinking / plan / subagent / reasoning]\n  ContextFlags --> LangGraphSubmit[thread.submit streamSubgraphs streamResumable]\n  useStream --> OnCreated[onCreated upsert busy thread]\n  useStream --> OnToolEnd[on_tool_end listener]\n  useStream --> OnUpdate[onUpdate title + summarization]\n  useStream --> OnCustom[task_running / llm_retry]\n  useStream --> OnError[clear optimistic + invalidate token usage]\n  useStream --> OnFinish[invalidate thread lists + token usage]\n  useThreadHistory --> Merge[mergeMessages]\n  useStream --> Merge\n  HumanOptimistic --> Merge\n```\n\n<callout emoji=\"💡\">\n`useThreadStream` 不只是 `useStream` 包装：它还承担 optimistic UI、文件上传、隐藏消息、mode 到运行上下文的映射、subtask/custom event 更新、错误清理和 React Query cache 失效。\n</callout>",
      "document_id": "LfIHdQPs4orPQxxjckXmM0nIytf",
      "revision_id": 20
    }
  }
}
