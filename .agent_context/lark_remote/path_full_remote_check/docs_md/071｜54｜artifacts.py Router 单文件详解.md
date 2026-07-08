{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>54｜artifacts.py Router 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清 artifacts.py 的接口职责、数据流和修改风险。\n</callout>\n\n# 1. 接口职责\n\n| 函数 | 职责 |\n|-|-|\n| `get_artifact` | 解析 virtual path 并返回文件响应。 |\n| `_extract_file_from_skill_archive` | 预览 .skill zip 内部文件。 |\n| `is_text_file_by_content` | 判断文本/二进制。 |\n| 主动内容保护 | HTML/SVG/XHTML 强制 attachment。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Request[artifact URL path] --> Resolve[resolve_thread_virtual_path]\n  Resolve --> Exists{file exists?}\n  Exists -->|no| NotFound\n  Exists -->|yes| Skill{inside skill archive?}\n  Skill -->|yes| Extract[extract zip member safely]\n  Skill -->|no| Mime[detect mimetype]\n  Mime --> Active{active content?}\n  Active -->|yes| Attachment[force download]\n  Active -->|no| Inline[inline or file response]\n```\n\n# 3. 修改建议\n\n- 先改 Pydantic request/response，再改 handler。\n- 涉及用户数据必须确认 owner check 或 current user。\n- 前端调用方要同步更新 core API/hook。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "LfAcdzwGoovGBKxt2Y3muPMFyRe",
      "revision_id": 17
    }
  }
}
