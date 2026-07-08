<title>54｜artifacts.py Router 单文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲清 artifacts.py 的接口职责、数据流和修改风险。
</callout>

# 1. 接口职责

| 函数 | 职责 |
|-|-|
| `get_artifact` | 解析 virtual path 并返回文件响应。 |
| `_extract_file_from_skill_archive` | 预览 .skill zip 内部文件。 |
| `is_text_file_by_content` | 判断文本/二进制。 |
| 主动内容保护 | HTML/SVG/XHTML 强制 attachment。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  Request[artifact URL path] --> Resolve[resolve_thread_virtual_path]
  Resolve --> Exists{file exists?}
  Exists -->|no| NotFound
  Exists -->|yes| Skill{inside skill archive?}
  Skill -->|yes| Extract[extract zip member safely]
  Skill -->|no| Mime[detect mimetype]
  Mime --> Active{active content?}
  Active -->|yes| Attachment[force download]
  Active -->|no| Inline[inline or file response]
```

# 3. 修改建议

- 先改 Pydantic request/response，再改 handler。
- 涉及用户数据必须确认 owner check 或 current user。
- 前端调用方要同步更新 core API/hook。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块采用 router/API 分层，是为了把 HTTP 边界、鉴权、请求响应模型和内部服务逻辑分开。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是接口职责清晰，前端和外部 SDK 可稳定调用。 |
| 代价 | 代价是一次业务流常跨 router、service、runtime、repository 多层。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/` 与 `backend/app/gateway/services.py`。 |
| 阅读路径 | 阅读路径：从 URL 路径找 router，再看 request model、authz、依赖注入和 service 调用。 |

```mermaid
flowchart TD
  A[设计动机] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[理解方式]
```