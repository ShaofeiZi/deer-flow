{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>135｜Scripts Setup/Dev/Deploy 脚本详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| check.py/doctor.py | 依赖和配置诊断。 |\n| configure.py/config-upgrade.sh | 生成和升级 config.yaml。 |\n| serve.sh | 本地 dev/prod 服务编排。 |\n| docker.sh | Docker 开发模式。 |\n| deploy.sh | 生产 Docker 编排。 |\n| setup_wizard.py | 交互式初始化。 |\n\n```mermaid\nflowchart TD\n  User --> Makefile\n  Makefile --> Check[check.py]\n  Makefile --> Doctor[doctor.py]\n  Makefile --> Config[configure.py]\n  Makefile --> Serve[serve.sh]\n  Serve --> Gateway[uvicorn gateway]\n  Serve --> Frontend[pnpm dev]\n  Serve --> Nginx[nginx]\n  Makefile --> Docker[docker.sh]\n  Makefile --> Deploy[deploy.sh]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "KzTudbQrso6iq1xv9oVm1IQGyfe",
      "revision_id": 16
    }
  }
}
