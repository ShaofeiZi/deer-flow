<title>107｜UI Navigation/Overlay Primitives 详解</title>

<callout emoji="✅">
**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| breadcrumb.tsx | 路径导航。 |
| dropdown-menu.tsx | 下拉菜单。 |
| hover-card.tsx | 悬浮卡。 |
| sheet.tsx | 抽屉。 |
| tabs.tsx | 标签页。 |
| collapsible.tsx | 折叠区域。 |

```mermaid
flowchart TD
  Navigation --> Breadcrumb
  Actions --> DropdownMenu
  HoverInfo --> HoverCard
  MobilePanel --> Sheet
  Sections --> Tabs
  Expandable --> Collapsible
  Workspace --> Navigation
  Settings --> Tabs
  Sidebar --> Collapsible
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档说明前端 UI primitive、workspace 组件或页面模块的职责、状态来源和渲染分支。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 组件边界清晰后，UI 问题可按 props/state/hook/route 快速定位。 |
| 代价 | 一次交互常跨页面、hook、context 和展示组件，需要按数据流追踪。 |
| 重点代码 | 标题对应的 `frontend/src/app/`、`frontend/src/components/` 或 `frontend/src/core/` 文件。 |
| 阅读路径 | 先看组件输入输出，再看状态来源，最后看事件回调如何改变 UI。 |

```mermaid
flowchart TD
  Cn["cn @/lib/utils"]
  Slot["@radix-ui/react-slot"]
  Cn --> Breadcrumb["breadcrumb.tsx"]
  Slot --> Breadcrumb
  Cn --> DM["DropdownMenu Root"]
  DM --> DMTr["Trigger"]
  DM --> DMPortal["Portal"]
  DMPortal --> DMContent["Content sideOffset"]
  DMContent --> DMItems["Item CheckboxItem RadioItem Sub"]
  Cn --> HC["HoverCard Root"]
  HC --> HCTr["HoverCardTrigger"]
  HC --> HCContent["HoverCardContent align sideOffset"]
  Cn --> SH["Sheet Root"]
  SH --> SHC["SheetTrigger SheetClose"]
  SH --> SHContent["SheetContent side"]
  SHContent --> SHOverlay["SheetOverlay inset-0 z-50"]
```