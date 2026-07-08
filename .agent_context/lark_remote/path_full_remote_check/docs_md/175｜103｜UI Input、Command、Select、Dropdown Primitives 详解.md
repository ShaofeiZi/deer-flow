{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 103｜UI Input、Command、Select、Dropdown Primitives 详解\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| input/textarea | 表单输入。 |\n| command.tsx | 命令面板和搜索。 |\n| select.tsx | 模型选择/设置项选择。 |\n| dropdown-menu.tsx | 菜单动作。 |\n| button/toggle | 按钮和开关交互。 |\n\n```mermaid\nflowchart TD\n  InputBox --> Textarea\n  ModelSelector --> Select\n  CommandPalette --> Command\n  WorkspaceMenu --> DropdownMenu\n  Settings --> Switch\n  Actions --> Button\n  Modes --> ToggleGroup\n```",
      "document_id": "VtUtduI0soRZZmxD3QfmogrXykT",
      "revision_id": 18
    }
  }
}
