<title>130｜Core Threads Stream、History、Cache 函数组详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| useThreadStream | 封装 useStream 和 sendMessage。 |
| mergeMessages | 合并 optimistic/history/stream messages。 |
| useThreadHistory | 读取历史 run messages。 |
| upsertThreadInSearchCache | 更新 thread 搜索缓存。 |
| useInfiniteThreads | 会话列表分页。 |

```mermaid
flowchart TD
  ChatPage --> useThreadStream
  useThreadStream --> useThreadHistory[load historical run messages]
  useThreadStream --> useStream[LangGraph useStream]
  UserSubmit --> sendMessage
  sendMessage --> Baseline[pending usage baseline]
  sendMessage --> Optimistic{hide_from_ui?}
  Optimistic -->|no| HumanOptimistic[optimistic human message]
  Optimistic -->|yes| NoOptimistic[skip visible optimistic row]
  sendMessage --> Uploads{files?}
  Uploads -->|yes| UploadFiles[convert + upload files]
  UploadFiles --> UploadedKwargs[additional_kwargs.files uploaded]
  Uploads -->|no| Submit
  UploadedKwargs --> Submit
  Submit --> ContextFlags[thinking / plan / subagent / reasoning]
  ContextFlags --> LangGraphSubmit[thread.submit streamSubgraphs streamResumable]
  useStream --> OnCreated[onCreated upsert busy thread]
  useStream --> OnToolEnd[on_tool_end listener]
  useStream --> OnUpdate[onUpdate title + summarization]
  useStream --> OnCustom[task_running / llm_retry]
  useStream --> OnError[clear optimistic + invalidate token usage]
  useStream --> OnFinish[invalidate thread lists + token usage]
  useThreadHistory --> Merge[mergeMessages]
  useStream --> Merge
  HumanOptimistic --> Merge
```


<callout emoji="💡">
`useThreadStream` 不只是 `useStream` 包装：它还承担 optimistic UI、文件上传、隐藏消息、mode 到运行上下文的映射、subtask/custom event 更新、错误清理和 React Query cache 失效。
</callout>
