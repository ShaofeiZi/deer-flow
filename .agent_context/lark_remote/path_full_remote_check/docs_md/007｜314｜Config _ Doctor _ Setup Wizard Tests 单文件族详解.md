{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>314｜Config / Doctor / Setup Wizard Tests 单文件族详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆更细 backend/frontend/skill scripts 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| test_doctor.py | doctor 脚本。 |\n| test_setup_wizard.py | setup wizard。 |\n| test_config_version.py | 配置版本。 |\n| test_app_config_reload.py | 配置热加载。 |\n| test_reload_boundary.py | 启动边界。 |\n\n```mermaid\nflowchart TD\n  ConfigCode --> ConfigTests\n  DoctorScript --> DoctorTests\n  SetupWizard --> WizardTests\n  ReloadBoundary --> BoundaryTests\n  ConfigTests --> Assertions\n  DoctorTests --> Assertions\n  WizardTests --> Assertions\n  Assertions --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明前端 UI primitive、workspace 组件或页面模块的职责、状态来源和渲染分支。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 组件边界清晰后，UI 问题可按 props/state/hook/route 快速定位。 |\n| 代价 | 一次交互常跨页面、hook、context 和展示组件，需要按数据流追踪。 |\n| 重点代码 | 标题对应的 `frontend/src/app/`、`frontend/src/components/` 或 `frontend/src/core/` 文件。 |\n| 阅读路径 | 先看组件输入输出，再看状态来源，最后看事件回调如何改变 UI。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "FCPLdM2jmoIXE6x2noRmzd8Lyrb",
      "revision_id": 18
    }
  }
}
