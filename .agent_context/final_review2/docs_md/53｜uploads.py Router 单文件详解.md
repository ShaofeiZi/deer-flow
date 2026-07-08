<title>53｜uploads.py Router 单文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲清 uploads.py 的接口职责、数据流和修改风险。
</callout>

# 1. 接口职责

| 接口 | 职责 |
|-|-|
| `POST uploads` | 写入文件、限额校验、可选转换 Markdown。 |
| `GET limits` | 返回上传限制。 |
| `GET list` | 列出 uploads。 |
| `DELETE filename` | 安全删除上传文件。 |

# 2. 运行逻辑图

```mermaid
sequenceDiagram
  participant UI as Frontend
  participant R as uploads.py
  participant FS as uploads dir
  participant Conv as converter
  UI->>R: multipart files
  R->>R: validate limits and filenames
  R->>FS: open no symlink and write chunks
  R->>Conv: optional convert to markdown
  Conv-->>FS: markdown file
  R-->>UI: UploadedFileInfo virtual path and artifact url
```

# 3. 修改建议

- 先改 Pydantic request/response，再改 handler。
- 涉及用户数据必须确认 owner check 或 current user。
- 前端调用方要同步更新 core API/hook。

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
