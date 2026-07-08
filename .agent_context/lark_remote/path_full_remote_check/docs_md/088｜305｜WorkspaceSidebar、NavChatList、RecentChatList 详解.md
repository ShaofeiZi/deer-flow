{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>305｜WorkspaceSidebar、NavChatList、RecentChatList 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 frontend workspace/chat/artifacts/messages 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| workspace-sidebar.tsx | 侧边栏总装。 |\n| workspace-nav-chat-list.tsx | 会话导航列表。 |\n| recent-chat-list.tsx | 最近会话。 |\n| workspace-nav-menu.tsx | 导航菜单。 |\n\n```mermaid\nflowchart TD\n  WorkspaceContent --> WorkspaceSidebar\n  WorkspaceSidebar --> NavMenu\n  WorkspaceSidebar --> NavChatList\n  NavChatList --> StaticLinks[Chats and Agents links]\n  RecentChatList --> useInfiniteThreads\n  useInfiniteThreads --> ThreadsAPI\n  WorkspaceSidebar --> RecentChatList\n  ThreadClick --> RouteChange\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**Workspace sidebar 把全局导航、最近会话分页、会话操作和设置入口集中在左侧，使 chat 页面只关注当前 thread 的内容区。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | chats/agents 主导航、最近会话、rename/delete/share/export 和 settings menu 都有统一入口。 |\n| 代价 | RecentChatList 同时处理分页、当前路由高亮、删除后的跳转、导出前取 state 等多种 UI 状态。 |\n| 重点代码 | `frontend/src/components/workspace/workspace-sidebar.tsx`、`workspace-nav-chat-list.tsx`、`recent-chat-list.tsx`、`workspace-nav-menu.tsx`。 |\n| 阅读路径 | 先看 sidebar 组合结构，再看 nav links，最后看 RecentChatList 的分页 sentinel、dropdown 操作和 route 选择。 |\n\n```mermaid\nflowchart TD\n  WorkspaceSidebar --> WorkspaceHeader\n  WorkspaceSidebar --> WorkspaceNavChatList\n  WorkspaceSidebar --> RecentChatList\n  WorkspaceSidebar --> WorkspaceNavMenu\n  RecentChatList --> useInfiniteThreads\n  RecentChatList --> RenameDeleteShareExport\n  RenameDeleteShareExport --> ThreadCaches\n  WorkspaceNavMenu --> SettingsDialog\n```",
      "document_id": "Tgu3djIbPoz3jaxqFYCmK8lsyVc",
      "revision_id": 18
    }
  }
}
