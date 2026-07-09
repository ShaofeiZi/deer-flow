<title>324｜Frontend Docs/Blog Routes 深拆</title>

<callout emoji="✅">
**本章目标：**继续拆 backend tests、frontend pages、docker/provisioner、wizard step 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| app/[lang]/docs/layout.tsx | Nextra docs layout。 |
| app/[lang]/docs/[[...mdxPath]]/page.tsx | docs page importPage。 |
| app/blog/layout.tsx | blog Nextra layout。 |
| app/blog/[[...mdxPath]]/page.tsx | blog page。 |
| app/blog/posts/page.tsx | 全部文章页。 |
| app/blog/tags/[tag]/page.tsx | 标签页。 |

```mermaid
flowchart TD
  DocsURL --> DocsLayout
  DocsLayout --> DocsPage
  DocsPage --> importPage
  BlogURL --> BlogLayout
  BlogLayout --> BlogPage
  BlogPage --> getAllPosts
  TagsURL --> TagPage
  TagPage --> filterByTag
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
sequenceDiagram
  participant Browser
  participant BlogLayout as "blog/layout.tsx"
  participant BlogPage as "blog/page.tsx"
  participant Core as "core/blog index.ts"
  participant Nextra as "nextra importPage"

  Browser->>BlogLayout: GET /blog
  BlogLayout->>Core: getBlogIndexData
  Core->>Core: getAllPosts mergePostsBySlug
  Core-->>BlogLayout: pageMap recentPosts tags
  BlogLayout-->>Browser: Nextra Layout sidebar

  Browser->>BlogPage: mdxPath params
  BlogPage->>BlogPage: getI18n getPreferredBlogLang
  alt mdxPath empty
    BlogPage->>Core: getAllPosts preferredLang
    Core-->>BlogPage: BlogPost list
    BlogPage-->>Browser: PostList All Posts
  else mdxPath tags
    BlogPage->>Core: getBlogIndexData tag filter
    Core-->>BlogPage: filtered posts
    alt posts empty
      BlogPage-->>Browser: notFound 404
    else
      BlogPage-->>Browser: PostList by tag
    end
  else mdxPath post slug
    BlogPage->>Nextra: importPage per BLOG_LANGS
    Nextra-->>BlogPage: localized pages
    BlogPage->>BlogPage: pick preferredLang else fallback
    BlogPage-->>Browser: MDXContent PostMeta
  end
```