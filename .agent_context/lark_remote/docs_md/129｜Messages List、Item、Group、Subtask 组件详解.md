<title>129｜Messages List、Item、Group、Subtask 组件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| message-list.tsx | 消息列表、历史加载、分组渲染。 |
| message-list-item.tsx | 单条消息。 |
| message-group.tsx | processing/reasoning/tool calls。 |
| subtask-card.tsx | task tool 状态。 |
| message-token-usage.tsx | 消息级 token usage。 |

```mermaid
flowchart TD
  ThreadMessages --> MessageList
  MessageList --> Groups[getMessageGroups]
  Groups --> Item[MessageListItem]
  Groups --> Group[MessageGroup]
  Groups --> Subtask[SubtaskCard]
  Groups --> TokenUsage[MessageTokenUsage]
  History[load more] --> MessageList
  SubtaskEvents --> SubtaskCard
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统中抽出来。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是学习和定位更聚焦。 |
| 代价 | 代价是章节数量更多，需要依赖目录维护。 |
| 重点代码 | 重点代码见本章列出的文件路径。 |
| 阅读路径 | 阅读路径：先看上游输入和下游输出，再读关键函数。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```