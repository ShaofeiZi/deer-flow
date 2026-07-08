<title>103｜UI Input、Command、Select、Dropdown Primitives 详解</title>

<callout emoji="✅">
**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| input/textarea | 表单输入。 |
| command.tsx | 命令面板和搜索。 |
| select.tsx | 模型选择/设置项选择。 |
| dropdown-menu.tsx | 菜单动作。 |
| button/toggle | 按钮和开关交互。 |

```mermaid
flowchart TD
  InputBox --> Textarea
  ModelSelector --> Select
  CommandPalette --> Command
  WorkspaceMenu --> DropdownMenu
  Settings --> Switch
  Actions --> Button
  Modes --> ToggleGroup
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