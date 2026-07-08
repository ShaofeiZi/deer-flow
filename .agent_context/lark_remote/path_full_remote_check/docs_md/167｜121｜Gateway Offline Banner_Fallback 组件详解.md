{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 121｜Gateway Offline Banner/Fallback 组件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续按 workspace 业务组件讲解职责、输入输出和运行逻辑。\n</callout>\n\n| 组件/文件 | 说明 |\n|-|-|\n| gateway-offline-banner.tsx | 顶部离线提示。 |\n| gateway-offline-fallback.tsx | Gateway 不可用时的整体 fallback。 |\n| gateway-offline-banner-helpers.ts | 离线检测辅助。 |\n| gateway-offline-fallback in layouts | auth/workspace layout 中兜底渲染。 |\n\n```mermaid\nflowchart TD\n  Layout --> ServerUser[getServerSideUser]\n  ServerUser --> Status{gateway unavailable?}\n  Status -->|yes| Fallback[GatewayOfflineFallback]\n  Status -->|no| Workspace[WorkspaceContent]\n  Workspace --> Banner[GatewayOfflineBanner]\n  Banner --> Retry[retry/check helper]\n  Fallback --> AuthProvider[temporary auth fallback]\n```",
      "document_id": "AJ0OdyjGloe8BZxuVLNmHiz8y27",
      "revision_id": 18
    }
  }
}
