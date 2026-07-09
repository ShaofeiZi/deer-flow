<title>127｜Account、Appearance、Notification、About Settings Pages 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| account-settings-page.tsx | 账号信息展示和账号操作入口。 |
| appearance-settings-page.tsx | 主题/外观设置。 |
| notification-settings-page.tsx | 浏览器通知偏好。 |
| about-settings-page.tsx | 版本/项目信息。 |

```mermaid
flowchart TD
  SettingsDialog --> Account
  SettingsDialog --> Appearance
  SettingsDialog --> Notification
  SettingsDialog --> About
  Account --> AuthProvider
  Appearance --> ThemeProvider
  Notification --> LocalSettings
  Notification --> BrowserPermission
  About --> AboutContent
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
sequenceDiagram
  participant Page as NotificationSettingsPage
  participant Notif as useNotification
  participant LS as useLocalSettings
  participant API as Notification API

  Page->>LS: set notification enabled
  LS->>LS: updateLocalSettings store
  Page->>Notif: requestPermission
  Notif->>API: Notification.requestPermission
  API-->>Notif: permission result
  Notif->>Page: setPermission state
  Page->>Notif: showNotification title body
  Notif->>LS: read notification.enabled
  Notif->>Notif: check 1s throttle
  Notif->>API: new Notification title opts
  API-->>Page: onclick focus close
```