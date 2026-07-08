{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>320｜Claude/Vercel/Find Skills Scripts 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆更细 backend/frontend/skill scripts 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| claude-to-deerflow/scripts/status.sh | 状态检查。 |\n| claude-to-deerflow/scripts/chat.sh | 聊天脚本。 |\n| vercel-deploy-claimable/scripts/deploy.sh | Vercel 部署。 |\n| find-skills/scripts/install-skill.sh | 安装 skill。 |\n\n```mermaid\nflowchart TD\n  ClaudeSkill --> StatusScript\n  ClaudeSkill --> ChatScript\n  VercelSkill --> DeployScript\n  FindSkills --> InstallSkillScript\n  DeployScript --> PublicURL\n  InstallSkillScript --> SkillsDir\n  ChatScript --> DeerFlowChat\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Q2TAdCnA7o8KVux0m6HmQGBjyzh",
      "revision_id": 16
    }
  }
}
