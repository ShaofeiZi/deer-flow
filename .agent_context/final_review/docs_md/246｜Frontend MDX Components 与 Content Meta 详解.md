<title>246｜Frontend MDX Components 与 Content Meta 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试 helper、fixtures、frontend content 支持模块。
</callout>

| 模块点 | 说明 |
|-|-|
| mdx-components.ts | MDX wrapper 与组件映射。 |
| content/\*/\_meta.ts | Nextra 目录元数据。 |
| content/\*/\*/\_meta.ts | 各子目录侧边栏顺序。 |
| getPageMap | 读取 Nextra page map。 |

```mermaid
flowchart TD
  MDXFile --> ImportPage
  ImportPage --> MDXComponents
  MetaFiles --> PageMap
  PageMap --> NextraLayout
  MDXComponents --> Wrapper
  Wrapper --> RenderedPage
  NextraLayout --> RenderedPage
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
  Req["GET /blog request"]
  Route["blog page.tsx"]
  Loc["getPreferredBlogLang"]
  GPM["getPageMap zh posts and en posts"]
  Collect["collectLocalizedBlogPosts"]
  Norm["normalizeBlogRoute to /blog"]
  Merge["mergePostsBySlug"]
  Pref["selectPreferredLanguage"]
  Sort["sort by date desc"]
  Data["BlogIndexData posts tags recent"]
  IP["importPage slug lang"]
  Wrap["useMDXComponents Wrapper"]
  Page["rendered blog page"]

  Req --> Route
  Route --> Loc
  Route --> GPM
  Loc --> Merge
  GPM --> Collect
  Collect --> Norm
  Norm --> Merge
  Merge --> Pref
  Pref --> Sort
  Sort --> Data
  Route --> IP
  Route --> Wrap
  IP --> Page
  Wrap --> Page
  Data --> Page
```