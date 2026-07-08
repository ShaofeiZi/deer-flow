{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>187｜OAuth / Memory / Sandbox / Detection Scripts 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| export_claude_code_oauth.py | 导出 Claude Code OAuth。 |\n| load_memory_sample.py | 加载 memory 示例。 |\n| setup-sandbox.sh | 预拉 sandbox 镜像。 |\n| sandbox_memory_profile.py | sandbox 内存画像。 |\n| detect_uv_extras.py | uv extras 检测。 |\n| tool-error-degradation-detection.sh | 工具错误降级检测。 |\n\n```mermaid\nflowchart TD\n  Dev --> OAuth[export oauth]\n  Dev --> Memory[load memory sample]\n  Dev --> SandboxSetup[setup sandbox]\n  Dev --> Profile[sandbox memory profile]\n  Dev --> DetectUV[detect uv extras]\n  Dev --> ToolErr[tool error degradation]\n  SandboxSetup --> Docker[pull image]\n  Memory --> MemoryJson[memory json]\n  Profile --> Report[profile report]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Gk4udjVLUojGoXxCgIWmMwwgyRd",
      "revision_id": 16
    }
  }
}
