<title>342｜Landing Header / Footer / Section 组件详解</title>

<callout emoji="✅">
**本章目标：**继续细化前端 UI/Landing/I18n 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| header.tsx | 首页顶部导航。 |
| footer.tsx | 页脚。 |
| section.tsx | 通用 section 布局。 |
| post-list.tsx | 文章列表组件。 |

```mermaid
flowchart TD
  LandingPage --> Header
  LandingPage --> Sections
  Sections --> SectionWrapper
  LandingPage --> Footer
  BlogPage --> PostList
  Header --> Navigation
  Footer --> Links
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 好处是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 坏处是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```