<title>228｜Frontend Content Reference/Application/Tutorials 分类详解</title>

<callout emoji="✅">
**本章目标：**继续拆剩余文档/content 模块，说明用途和关联运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| reference | 模型 providers/API 参考。 |
| application | 应用场景文档。 |
| tutorials | 教程。 |
| posts | 博客文章。 |
| meta files | \_meta.ts 控制目录。 |

```mermaid
flowchart TD
  Content --> Reference
  Content --> Application
  Content --> Tutorials
  Content --> Posts
  Meta[_meta ts] --> NextraPageMap
  Reference --> DocsSite
  Application --> DocsSite
  Tutorials --> DocsSite
  Posts --> Blog
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  NextCfg["next.config.js withNextra"] --> Build["Nextra build"]
  Root["content/en/_meta.ts"] --> Build
  Build --> PageMap["Nextra PageMap"]
  RefMeta["reference/_meta.ts model-providers"] --> RefSec["Reference section"]
  AppMeta["application/_meta.ts quick-start configuration"] --> AppSec["Application section"]
  TutMeta["tutorials/_meta.ts first-conversation"] --> TutSec["Tutorials section"]
  PostsMeta["posts/_meta.ts weekly"] --> BlogSec["Blog section"]
  PageMap --> Sidebar["Sidebar navigation"]
  RefSec --> Sidebar
  AppSec --> Sidebar
  TutSec --> Sidebar
  BlogSec --> BlogPage["Blog index page"]
```