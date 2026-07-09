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
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart LR
  Dialog["dialog.tsx"]
  Sheet["sheet.tsx"]
  Tooltip["tooltip.tsx"]
  Command["command.tsx"]
  InputGroup["input-group.tsx"]
  ButtonGroup["button-group.tsx"]

  RadixDialog["@radix-ui/react-dialog"]
  RadixTooltip["@radix-ui/react-tooltip"]
  Cmdk["cmdk"]
  Utils["lib/utils cn"]
  CVA["class-variance-authority"]

  Button["button.tsx"]
  Input["input.tsx"]
  Textarea["textarea.tsx"]
  Separator["separator.tsx"]
  Slot["@radix-ui/react-slot"]

  Dialog --> RadixDialog
  Dialog --> Utils
  Sheet --> RadixDialog
  Sheet --> Utils
  Tooltip --> RadixTooltip
  Tooltip --> Utils
  Command --> Cmdk
  Command --> Dialog
  Command --> Utils
  InputGroup --> Button
  InputGroup --> Input
  InputGroup --> Textarea
  InputGroup --> Utils
  InputGroup --> CVA
  ButtonGroup --> Separator
  ButtonGroup --> Utils
  ButtonGroup --> CVA
  ButtonGroup --> Slot
```