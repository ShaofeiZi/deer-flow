<title>230｜Frontend Content Introduction Docs 详解</title>

<callout emoji="✅">
**本章目标：**继续细化 content/spec/docs 单模块，补充运行/维护逻辑图。
</callout>

| 模块点 | 说明 |
|-|-|
| content/en/introduction | 英文 introduction 文档。 |
| content/zh/introduction | 中文 introduction 文档。 |
| \_meta.ts | 控制目录和排序。 |
| Nextra routing | 由 app/[lang]/docs 加载。 |

```mermaid
flowchart TD
  IntroFiles[content introduction] --> Meta[_meta ts]
  IntroFiles --> ImportPage[Nextra importPage]
  Meta --> PageMap
  ImportPage --> MDX
  MDX --> DocsLayout
  DocsLayout --> Browser
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
  Req["Browser request docs introduction"] --> Page["page.tsx catch-all mdxPath"]
  Page --> GSP["generateStaticParamsFor"]
  Page --> IP["importPage mdxPath lang"]
  IP --> MDX["content lang introduction MDX"]
  MDX --> Meta["_meta.ts"]
  Meta --> SB["title and order for sidebar"]
  IP --> Wrap["mdx-components.ts wrapper"]
  Wrap --> Out["MDXContent toc metadata"]
  Out --> Layout["layout.tsx DocLayout"]
  Layout --> GPM["getPageMap slash lang"]
  GPM --> FPR["formatPageRoute slash lang docs"]
  FPR --> PM["pageMap sidebar nav"]
  Layout --> Loc["getLocaleByLang lang"]
  Loc --> Theme["Layout nextra-theme-docs"]
  PM --> Theme
  Out --> Theme
  Theme --> Chrome["Header and Footer landing"]
  Theme --> Browser["Browser renders docs page"]
```