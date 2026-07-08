{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>136｜Scripts Diagnostics/Maintenance 脚本详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| detect_blocking_io_static.py | 静态扫描阻塞 IO。 |\n| detect_thread_boundaries.py | 线程/异步边界清单。 |\n| sandbox_memory_profile.py | sandbox 内存画像。 |\n| tool-error-degradation-detection.sh | 工具错误降级检测。 |\n| cleanup-containers.sh | 清理容器。 |\n| sync_labels.py | 同步 issue labels。 |\n\n```mermaid\nflowchart TD\n  Dev[developer] --> Diagnose[diagnostic scripts]\n  Diagnose --> Blocking[detect blocking IO]\n  Diagnose --> Threads[detect thread boundaries]\n  Diagnose --> SandboxMem[sandbox memory profile]\n  Diagnose --> ToolErrors[tool error degradation]\n  Maintenance[maintenance] --> Cleanup[cleanup containers]\n  Maintenance --> Labels[sync labels]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "W07EdWJpWooeyOxpPa0mO8MWyhg",
      "revision_id": 16
    }
  }
}
