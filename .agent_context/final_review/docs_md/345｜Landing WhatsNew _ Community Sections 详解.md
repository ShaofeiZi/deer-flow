<title>345｜Landing WhatsNew / Community Sections 详解</title>

<callout emoji="✅">
**本章目标：**继续细化前端 UI/Landing/I18n 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| whats-new-section.tsx | 版本亮点/新能力。 |
| community-section.tsx | 社区和贡献入口。 |
| github link | 引导 GitHub。 |
| docs link | 引导文档。 |

```mermaid
flowchart TD
  LandingPage --> WhatsNew
  LandingPage --> Community
  WhatsNew --> FeatureHighlights
  Community --> GitHub
  Community --> Docs
  Community --> Contribution
  FeatureHighlights --> CTA
  Contribution --> UserEngagement
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart TD
  Page["app/page.tsx LandingPage"]
  WhatsNew["whats-new-section"]
  Community["community-section"]
  Section["section.tsx"]
  Bento["ui/magic-bento"]
  Features["features BentoCardProps"]
  Aurora["ui/aurora-text"]
  Button["ui/button"]
  Link["next/link GitHub"]
  Radix["radix GitHubLogoIcon"]

  Page --> WhatsNew
  Page --> Community
  WhatsNew --> Section
  WhatsNew --> Bento
  WhatsNew --> Features
  Bento --> Features
  Community --> Section
  Community --> Aurora
  Community --> Button
  Community --> Radix
  Button --> Link
```