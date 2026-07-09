<title>102｜UI Layout Primitives：Sidebar、Resizable、ScrollArea、Dialog 详解</title>

<callout emoji="✅">
**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| sidebar.tsx | workspace sidebar 布局 primitive。 |
| resizable.tsx | ChatBox 左右分栏。 |
| scroll-area.tsx | 消息列表和设置页滚动容器。 |
| dialog/sheet | Settings、弹窗与抽屉。 |

```mermaid
flowchart TD
  WorkspaceContent --> Sidebar
  ChatBox --> ResizablePanelGroup
  MessageList --> ScrollArea
  SettingsTrigger --> Dialog
  MobilePanel --> Sheet
  Sidebar --> NavMenu
  ResizablePanelGroup --> ArtifactPanel
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
flowchart TD
  SidebarProvider["SidebarProvider"] --> SidebarContext["SidebarContext"]
  SidebarContext --> useSidebar["useSidebar"]
  SidebarProvider --> Sidebar["Sidebar desktop panel"]
  SidebarProvider --> Sheet["Sheet mobile drawer"]
  Sidebar --> WorkspaceSidebar["WorkspaceSidebar"]
  Sheet --> WorkspaceSidebar
  ResizablePanelGroup["ResizablePanelGroup"] --> ChatBox["ChatBox"]
  ChatBox --> ChatPanel["chat panel"]
  ChatBox --> ArtifactsPanel["artifacts panel"]
  Dialog["Dialog"] --> SettingsDialog["SettingsDialog"]
  ScrollArea["ScrollArea"] --> SettingsDialog
```