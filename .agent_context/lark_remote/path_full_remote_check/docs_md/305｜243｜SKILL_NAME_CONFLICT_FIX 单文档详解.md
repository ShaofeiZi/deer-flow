{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>243｜SKILL_NAME_CONFLICT_FIX 单文档详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化 content/docs/evidence 模块并给出维护逻辑图。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| SKILL_NAME_CONFLICT_FIX.md | skill 命名冲突修复说明。 |\n| 关联代码 | skills parser/storage/router。 |\n| 风险 | 同名 skill path/category 冲突。 |\n| 验证 | skills loader/parser/custom router tests。 |\n\n```mermaid\nflowchart TD\n  Conflict[skill name conflict] --> Doc[fix doc]\n  Doc --> Parser[skills parser]\n  Doc --> Storage[skill storage]\n  Doc --> Router[skills router]\n  Parser --> Tests[skills tests]\n  Storage --> Tests\n  Router --> Tests\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "L1oOd5AwBoahdux67yMmjOtoyJe",
      "revision_id": 16
    }
  }
}
