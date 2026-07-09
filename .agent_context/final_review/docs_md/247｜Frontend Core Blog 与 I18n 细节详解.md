<title>247｜Frontend Core Blog 与 I18n 细节详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试 helper、fixtures、frontend content 支持模块。
</callout>

| 模块点 | 说明 |
|-|-|
| core/blog/index.ts | 读取 posts、tags、preferred language。 |
| core/i18n/server.ts | 服务端 locale 检测。 |
| core/i18n/context.tsx | I18nProvider。 |
| core/i18n/translations.ts | 翻译聚合。 |
| locales/en-US zh-CN | 语言包。 |

```mermaid
flowchart TD
  Request --> DetectLocale
  DetectLocale --> I18nProvider
  I18nProvider --> UITranslations
  BlogRoute --> BlogCore
  BlogCore --> PreferredLang
  PreferredLang --> Posts
  Posts --> PostList
  Locales --> UITranslations
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
  Req["GET /blog request"] --> Srv["detectLocaleServer"]
  Srv --> Cookie["locale cookie"]
  Cookie --> Norm["normalizeLocale"]
  Norm --> I18n["getI18n / locale"]
  I18n --> Pref["getPreferredBlogLang"]
  Pref --> All["getAllPosts cached"]
  All --> PMzh["getPageMap /zh/posts"]
  All --> PMen["getPageMap /en/posts"]
  PMzh --> Collect["collectLocalizedBlogPosts"]
  PMen --> Collect
  Collect --> Merge["mergePostsBySlug"]
  Merge --> Sel["selectPreferredLanguage"]
  Sel --> Sorted["BlogPost[] sorted by date"]
  Sorted --> Routes["/blog posts and tags routes"]
  Routes --> List["PostList component"]
```