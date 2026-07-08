<title>81｜Nextra Docs、Content 与 Blog 渲染详解</title>

<callout emoji="✅">
**本章目标：**讲清文档站、博客、content 多语言内容如何被路由加载。
</callout>

| 模块点 | 说明 |
|-|-|
| Docs route | `app/[lang]/docs/[[...mdxPath]]` 调 importPage。 |
| Docs layout | Nextra Layout + pageMap + i18n。 |
| Blog route | `app/blog` 读取 posts/tags。 |
| Content | `src/content/en\|zh` 存放 MDX。 |
| MDX components | 统一 wrapper 和组件。 |

```mermaid
flowchart TD
  URL[docs or blog URL] --> Route[Next app route]
  Route --> Locale[detect preferred lang]
  Locale --> Import[importPage or getAllPosts]
  Import --> Content[MDX content]
  Content --> Wrapper[MDX components wrapper]
  Wrapper --> Nextra[Nextra Layout]
  Nextra --> Browser[rendered page]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块承担 agent 扩展能力，是为了把工具、知识、长期上下文或执行环境做成可组合部件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可扩展、可配置、可替换。 |
| 代价 | 代价是配置、prompt、工具 schema、外部服务任一环节出错都会影响结果。 |
| 重点代码 | 重点代码在 `backend/packages/harness/deerflow` 下对应 skills/mcp/memory/sandbox/tools/models 模块。 |
| 阅读路径 | 阅读路径：明确它给 agent 增加了什么能力，以及该能力在哪里被注入。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```