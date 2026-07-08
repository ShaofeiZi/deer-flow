{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>20｜Middleware 上下文与 UX 类文件详解：Dynamic、Skill、Summary、Todo、Title、Memory</title>\n\n<callout emoji=\"✅\">\n**本章目标：**把影响 prompt、上下文、标题、Todo、长期记忆的 middleware 拆开讲。\n</callout>\n\n# 1. 模块职责\n\n| 文件 | 职责 | 用户可见影响 |\n|-|-|-|\n| `dynamic_context_middleware.py` | 注入当前日期、memory reminder 等动态上下文 | 回答会带当前日期和个性化上下文。 |\n| `skill_activation_middleware.py` | 识别 /skill-name 并读取完整 SKILL.md | 显式 skill 激活更稳定。 |\n| `summarization_middleware.py` | 上下文接近限制时摘要，并保护 skill 内容 | 长对话不容易爆上下文。 |\n| `todo_middleware.py` | plan mode 中维护任务列表 | 前端 TodoList 展示进度。 |\n| `title_middleware.py` | 生成会话标题 | 侧边栏 thread title。 |\n| `memory_middleware.py` | after_agent 入队更新长期记忆 | 后续对话更个性化。 |\n\n# 2. 上下文注入与更新链路\n\n# 3. 调试建议\n\n- skill 没生效：查 slash 解析和 available_skills。\n- Todo 不显示：检查 is_plan_mode 和 `todos` state。\n- 标题不更新：看 TitleMiddleware 模型调用和 thread meta 同步。\n- memory 污染：看 message_processing 和 updater 的过滤规则。\n\n## 补充：Context 与 UX Middleware 简化运行图\n\n```mermaid\nflowchart TD\n  A[User Message] --> B[Dynamic Context]\n  B --> C[Skill Activation]\n  C --> D[Summarization]\n  D --> E[Todo Middleware]\n  E --> F[LLM Model]\n  F --> G[Title Middleware]\n  G --> H[Memory Middleware]\n  H --> I[Memory Queue]\n  F --> J[Final Assistant Message]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "JcBLdKkKro44LfxcRmjmkANvypd",
      "revision_id": 18
    }
  }
}
