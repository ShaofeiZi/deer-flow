<title>310｜Remaining UI Overlay/Input Primitives 详解</title>

<callout emoji="✅">
**本章目标：**补齐剩余 frontend/UI/misc 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| dialog.tsx | 对话框。 |
| sheet.tsx | 抽屉。 |
| tooltip.tsx | 提示。 |
| command.tsx | 命令面板。 |
| input-group.tsx | 输入组。 |
| button-group.tsx | 按钮组。 |

```mermaid
flowchart TD
  ModalNeed --> Dialog
  SidePanelNeed --> Sheet
  HoverInfo --> Tooltip
  SearchAction --> Command
  FormLayout --> InputGroup
  ActionGroup --> ButtonGroup
  Dialog --> SettingsDialog
  Command --> CommandPalette
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 好处是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 坏处是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```