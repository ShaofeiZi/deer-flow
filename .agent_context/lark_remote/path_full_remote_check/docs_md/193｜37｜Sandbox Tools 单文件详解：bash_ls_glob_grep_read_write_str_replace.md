{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>37｜Sandbox Tools 单文件详解：bash/ls/glob/grep/read/write/str_replace</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 sandbox/tools.py 中每个工具如何校验路径、替换虚拟路径、执行并截断输出。\n</callout>\n\n## 本轮源码校准补充：Sandbox Tools 路径与安全\n\n| 能力 | 安全边界 |\n|-|-|\n| `bash` | LocalSandbox 默认可能禁用或受配置限制；容器 sandbox 更适合执行命令。 |\n| `read_file` / `write_file` / `str_replace` | 通过虚拟路径解析，拒绝目录穿越和非法 host path。 |\n| MCP filesystem paths | 仅允许配置允许的路径集合。 |\n| custom mounts / ACP workspace | 需要经过 runtime path/config 映射，不应硬编码绝对路径。 |\n| output limit | 工具输出会被预算/截断策略保护，避免把大文件直接塞回模型上下文。 |\n\n| 工具 | 职责 |\n|-|-|\n| `bash` | 执行命令，LocalSandbox 下校验 host bash 和绝对路径。 |\n| `ls` | 列目录并截断输出。 |\n| `glob` | 按模式找文件，限制结果数。 |\n| `grep` | 全文搜索，跳过二进制和忽略路径。 |\n| `read_file` | 读取文件并截断过长内容。 |\n| `write_file` | 写入/追加文件，限制单次写入大小。 |\n| `str_replace` | 读改写串行化，避免并发写冲突。 |\n\n```mermaid\nflowchart TD\n  ToolCall[tool call] --> Runtime[get thread_data and sandbox]\n  Runtime --> Path[replace virtual path]\n  Path --> Validate[validate path and traversal]\n  Validate --> Sandbox[execute/read/write/list]\n  Sandbox --> Output[raw output]\n  Output --> Mask[mask local paths back to virtual]\n  Mask --> Truncate[truncate output]\n  Truncate --> ToolMessage[return to agent]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是查找和学习更快，职责更聚焦。 |\n| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |\n| 重点代码 | 重点代码见本章表格列出的源码路径。 |\n| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "SmrFdFwMYoZ1rSxcEWRm3aTSyVc",
      "revision_id": 17
    }
  }
}
