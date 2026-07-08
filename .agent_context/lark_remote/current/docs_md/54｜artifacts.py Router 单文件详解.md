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