{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 222｜docs/pr-evidence 证据材料详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。\n</callout>\n\n| 文档点 | 说明 |\n|-|-|\n| docs/pr-evidence | PR 截图/证据目录。 |\n| session-skill-manage-e2e | skill manage E2E 证据。 |\n| skill-manage-e2e | 技能管理页面证据。 |\n| 用途 | PR review 验证 UI/功能。 |\n\n```mermaid\nflowchart TD\n  FeatureChange --> ManualOrE2E[manual or e2e verification]\n  ManualOrE2E --> Screenshot[pr evidence screenshots]\n  Screenshot --> PR[Pull request]\n  PR --> Reviewer[reviewer checks evidence]\n  Reviewer --> Decision[merge decision]\n```",
      "document_id": "J42FddMalo1l51x8R3DmEdfayxh",
      "revision_id": 18
    }
  }
}
