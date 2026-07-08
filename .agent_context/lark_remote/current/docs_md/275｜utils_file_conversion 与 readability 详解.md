<title>275｜utils/file_conversion 与 readability 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 tools/reflection/utils 等基础模块。
</callout>

| 模块点 | 说明 |
|-|-|
| file_conversion.py | PDF/Office/表格等上传文件转 Markdown。 |
| readability.py | 网页/文本可读性处理。 |
| uploads router | 上传后可选调用转换。 |
| UploadsMiddleware | 读取转换出的 .md outline。 |

```mermaid
flowchart TD
  UploadFile --> Convert[file_conversion]
  Convert --> Markdown[markdown sibling file]
  Markdown --> Outline[extract outline]
  Outline --> UploadsMiddleware
  WebContent --> Readability
  Readability --> CleanText
  CleanText --> AgentContext
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