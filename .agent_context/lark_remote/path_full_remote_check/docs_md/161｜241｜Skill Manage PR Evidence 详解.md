{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 241｜Skill Manage PR Evidence 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化 content/docs/evidence 模块并给出维护逻辑图。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| skill-manage-e2e screenshot | 技能管理 E2E 截图。 |\n| session-skill-manage-e2e screenshot | 会话技能管理截图。 |\n| 用途 | 证明 UI/功能回归通过。 |\n| 关联 | skills router、settings skill page、artifact install。 |\n\n```mermaid\nflowchart TD\n  SkillFeature --> E2ETest\n  E2ETest --> Screenshot\n  Screenshot --> PREvidence\n  PREvidence --> Reviewer\n  Reviewer --> Confidence\n  SkillSettings --> SkillFeature\n  SkillsRouter --> SkillFeature\n```",
      "document_id": "X0JMdixjpoZUjpxzImIm5kJzyec",
      "revision_id": 18
    }
  }
}
