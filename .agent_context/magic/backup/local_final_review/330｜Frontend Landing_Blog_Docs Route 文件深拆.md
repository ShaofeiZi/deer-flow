<title>330｜Frontend Landing/Blog/Docs Route 文件深拆</title>

<callout emoji="✅">
**本章目标：**继续拆 remaining route/content/docker/script 内部模块。
</callout>

| 模块点 | 说明 |
|-|-|
| app/page.tsx | landing page 装配。 |
| app/blog/layout.tsx | blog layout。 |
| app/blog/posts/page.tsx | posts index。 |
| app/blog/tags/[tag]/page.tsx | tag page。 |
| app/[lang]/docs/layout.tsx | docs layout。 |

```mermaid
flowchart TD
  RootURL --> LandingPage
  LandingPage --> LandingSections
  BlogURL --> BlogLayout
  BlogLayout --> PostsPage
  BlogLayout --> TagPage
  DocsURL --> DocsLayout
  DocsLayout --> DocsPage
  DocsPage --> importPage
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
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```