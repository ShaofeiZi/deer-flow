<title>227｜Frontend Content Introduction/Harness 文档分类详解</title>

<callout emoji="✅">
**本章目标：**继续拆剩余文档/content 模块，说明用途和关联运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| content/en/introduction | 英文介绍文档。 |
| content/zh/introduction | 中文介绍文档。 |
| content/en/harness | 英文 harness 文档。 |
| content/zh/harness | 中文 harness 文档。 |
| Nextra | 渲染这些 content。 |

```mermaid
flowchart TD
  ContentDirs --> IntroEN
  ContentDirs --> IntroZH
  ContentDirs --> HarnessEN
  ContentDirs --> HarnessZH
  IntroEN --> Nextra
  IntroZH --> Nextra
  HarnessEN --> Nextra
  HarnessZH --> Nextra
  Nextra --> DocsSite
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
  Req["GET /:lang/docs/:mdxPath"] --> Root["app/layout.tsx"]
  Root --> Detect["detectLocaleServer"]
  Detect --> Cookie["locale cookie"]
  Cookie --> Norm["normalizeLocale"]
  Norm --> I18nProv["I18nProvider"]
  Root --> DocsLayout["docs/layout.tsx"]
  DocsLayout --> GetLocale["getLocaleByHang"]
  DocsLayout --> PageMap["getPageMap /:lang"]
  PageMap --> Meta["content/:lang/_meta.ts"]
  Meta --> Intro["introduction/*.mdx"]
  Meta --> Harness["harness/*.mdx"]
  DocsLayout --> Format["formatPageRoute /:lang/docs"]
  Format --> NextraLayout["nextra-theme-docs Layout"]
  DocsPage["docs/[[...mdxPath]]/page.tsx"] --> Import["importPage mdxPath lang"]
  Import --> MDX["MDXContent toc metadata"]
  MDX --> Wrapper["mdx-components.ts wrapper"]
  Wrapper --> NextraLayout
  NextraLayout --> Site["DocsSite"]
```