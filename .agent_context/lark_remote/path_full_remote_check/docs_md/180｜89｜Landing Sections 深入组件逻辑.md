{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 89｜Landing Sections 深入组件逻辑\n\n<callout emoji=\"✅\">\n**本章目标：**进一步拆首页每个 section 的组织方式和职责。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| hero.tsx | 主视觉、品牌口号、CTA。 |\n| case-study-section.tsx | 案例展示区。 |\n| skills-section.tsx | skills 能力和动画展示。 |\n| sandbox-section.tsx | sandbox 隔离执行能力展示。 |\n| whats-new-section.tsx | 版本亮点。 |\n| community-section.tsx | 社区和参与入口。 |\n\n```mermaid\nflowchart TD\n  LandingPage --> Header\n  LandingPage --> Hero\n  LandingPage --> CaseStudy\n  LandingPage --> Skills\n  Skills --> ProgressiveAnimation\n  LandingPage --> Sandbox\n  LandingPage --> WhatsNew\n  LandingPage --> Community\n  LandingPage --> Footer\n  SectionComponent --> SharedLayout[Section wrapper styles]\n```",
      "document_id": "UBupdd0huofiFzx7kwQma6Jbytc",
      "revision_id": 23
    }
  }
}
