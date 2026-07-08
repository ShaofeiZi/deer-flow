<title>74｜Frontend AI Elements 与 UI 基础组件详解</title>

<callout emoji="✅">
**本章目标：**讲清 ai-elements 与 workspace UI 基础组件如何支撑聊天体验。
</callout>

# 1. 模块职责

| 模块 | 说明 |
|-|-|
| ai-elements | message、conversation、prompt-input、artifact、reasoning、task、sources 等 AI UI primitive。 |
| ui components | button、dialog、sidebar、scroll-area、select 等 shadcn/radix 风格组件。 |
| workspace components | 在 ai-elements 和 ui 基础上组合业务 UI。 |
| streamdown | Markdown、Mermaid、KaTeX、代码高亮渲染。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  Design[UI primitives] --> UI[components ui]
  AI[AI Elements] --> Workspace[workspace components]
  UI --> Workspace
  Streamdown[core streamdown] --> Markdown[MarkdownContent]
  Markdown --> Message[MessageListItem]
  Prompt[PromptInput] --> InputBox
  Artifact[AI artifact primitives] --> ArtifactPanel
  Workspace --> ChatPage
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