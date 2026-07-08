{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>240｜Sandbox Memory Profiling / Blocking IO Docs 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化 content/docs/evidence 模块并给出维护逻辑图。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| SANDBOX_MEMORY_PROFILING.md | sandbox 内存分析说明。 |\n| BLOCKING_IO_DETECTION.md | 阻塞 IO 检测说明。 |\n| sandbox_memory_profile.py | 内存画像脚本。 |\n| detect_blocking_io_static.py | 阻塞 IO 静态检测。 |\n\n```mermaid\nflowchart TD\n  PerformanceIssue --> MemoryProfileDoc\n  PerformanceIssue --> BlockingIODoc\n  MemoryProfileDoc --> ProfileScript\n  BlockingIODoc --> DetectScript\n  ProfileScript --> MemoryReport\n  DetectScript --> BlockingReport\n  BlockingReport --> BlockingTests\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |\n| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |\n| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |\n| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "GQDjdom6Qo2tkrxLphjmfeKEyub",
      "revision_id": 18
    }
  }
}
