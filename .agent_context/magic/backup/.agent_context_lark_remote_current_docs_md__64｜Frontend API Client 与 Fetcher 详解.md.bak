<title>64｜Frontend API Client 与 Fetcher 详解</title>

<callout emoji="✅">
**本章目标：**讲清 LangGraph SDK client、CSRF 注入、普通 REST fetcher 和 stream mode 清洗。
</callout>

# 1. 模块职责

| 对象 | 说明 |
|-|-|
| `api-client.ts` | 创建 LangGraphClient，包装 runs.stream/joinStream。 |
| `fetcher.ts` | 普通 REST fetch，自动带 credentials/CSRF。 |
| `stream-mode.ts` | 过滤不支持的 stream modes。 |
| `config/index.ts` | 解析 Backend/LangGraph base URL。 |
| `static-mode` | 静态站点 mock client fallback。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  UI[Frontend Hook] --> Client[getAPIClient]
  Client --> Base[getLangGraphBaseURL]
  Client --> CSRF[inject X CSRF Token]
  Client --> SDK[LangGraphClient]
  SDK --> Stream[run stream]
  Stream --> Sanitize[sanitize stream modes]
  Rest[REST hooks] --> Fetcher[fetchWithAuth]
  Fetcher --> CSRF2[get csrf headers]
  Fetcher --> Gateway[Gateway API]
```

# 3. 排障与修改建议

- 先确认调用方和数据源，再改 schema。
- 涉及用户数据必须确认鉴权和 owner check。
- 涉及缓存需要同步 invalidate 或 reset。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |
| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |
| 重点代码 | 标题对应的源码、测试或文档入口。 |
| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |

```mermaid
flowchart TD
  A[设计目的] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```