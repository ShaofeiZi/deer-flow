<title>115｜UI Form Primitives：Button、Input、Textarea、Switch、Toggle 详解</title>

<callout emoji="✅">
**本章目标：**继续按小模块解释职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| button.tsx | 基础按钮。 |
| input.tsx | 单行输入。 |
| textarea.tsx | 多行输入。 |
| switch.tsx | 布尔开关。 |
| toggle/toggle-group | 模式切换。 |
| button-group/input-group | 组合控件。 |

```mermaid
flowchart TD
  FormState --> Input
  FormState --> Textarea
  BooleanState --> Switch
  ModeState --> ToggleGroup
  Action --> Button
  Grouped --> InputGroup
  Grouped --> ButtonGroup
  Components --> Settings
  Components --> InputBox
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart LR
  Utils["cn in lib/utils"] --> Button
  Utils --> Input
  Utils --> Textarea
  Utils --> Switch
  Utils --> Toggle
  Utils --> InputGroup
  Utils --> ButtonGroup
  CVA["cva buttonVariants"] --> Button
  CVA2["cva toggleVariants"] --> Toggle
  Toggle -- "exports toggleVariants" --> ToggleGroup
  ToggleGroup -- "ToggleGroupContext" --> ToggleGroupItem
  Button -- "asChild Slot" --> ConfettiButton
  Button --> InputGroupButton
  Input --> InputGroupInput
  Textarea --> InputGroupTextarea
  InputGroupButton --> InputGroup
  InputGroupInput --> InputGroup
  InputGroupTextarea --> InputGroup
  Separator --> ButtonGroupSeparator
  ButtonGroupSeparator --> ButtonGroup
  SwitchRoot["@radix Switch.Root"] --> Switch
  ToggleRoot["@radix Toggle.Root"] --> Toggle
  ToggleGroupRoot["@radix ToggleGroup.Root"] --> ToggleGroup
```