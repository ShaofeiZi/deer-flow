{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>24｜ThreadDataMiddleware 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清 ThreadDataMiddleware 如何解析 thread_id/user_id，如何创建并写入 thread_data。\n</callout>\n\n## 本轮源码校准补充：ThreadDataMiddleware\n\n<callout emoji=\"💡\">\n**作用：**为每个 thread 准备隔离的 user-data 目录结构，让 uploads、workspace、outputs 可以被 sandbox 和工具用统一虚拟路径访问。\n</callout>\n\n| 读源码重点 | 说明 |\n|-|-|\n| thread id | 线程 ID 是目录隔离的核心键。 |\n| virtual path | 前端/agent 看到的是 `/mnt/user-data/...` 这类虚拟路径，后端负责映射到实际目录。 |\n| 后续依赖 | UploadsMiddleware、SandboxMiddleware、artifact router 都依赖同一套路径约定。 |\n\n| 点 | 说明 |\n|-|-|\n| 入口 | `before_agent` |\n| 状态 | 写入 `thread_data.workspace_path/uploads_path/outputs_path` |\n| 隔离 | 使用 `get_effective_user_id()` 进入 per-user 目录 |\n| 额外行为 | 给最后一条 HumanMessage 补 run_id 和 timestamp |\n\n```mermaid\nflowchart TD\n  A[before_agent] --> B{thread_id in runtime context?}\n  B -->|yes| C[use thread_id]\n  B -->|no| D[read config.configurable.thread_id]\n  D --> E{missing?}\n  E -->|yes| F[raise ValueError]\n  E -->|no| C\n  C --> G[get_effective_user_id]\n  G --> H{lazy_init?}\n  H -->|yes| I[compute paths only]\n  H -->|no| J[ensure_thread_dirs]\n  I --> K[return thread_data]\n  J --> K\n  K --> L[patch last HumanMessage metadata]\n```\n\n# 新同学阅读建议\n\n先看 `_get_thread_paths` 和 `before_agent`，再顺着 `Paths.sandbox_*_dir` 理解物理目录。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |\n| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |\n| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |\n| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "UvKWdlU67ov47kx6ygsmR4FkyKd",
      "revision_id": 17
    }
  }
}
