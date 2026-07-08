<title>329｜Frontend Chats List Route 深拆</title>

<callout emoji="✅">
**本章目标：**继续拆 remaining route/content/docker/script 内部模块。
</callout>

| 模块点 | 说明 |
|-|-|
| workspace/chats/page.tsx | 会话列表页。 |
| useInfiniteThreads | 分页加载 threads。 |
| search filter | 本地标题搜索。 |
| sentinel | IntersectionObserver 自动加载。 |
| pathOfThread/titleOfThread | thread 工具函数。 |

```mermaid
flowchart TD
  ChatsPage --> UseInfiniteThreads
  UseInfiniteThreads --> ThreadSearchAPI
  ThreadSearchAPI --> Pages
  Pages --> FlattenThreads
  SearchInput --> FilterThreads
  Sentinel --> FetchNextPage
  ThreadClick --> ChatRoute
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