<title>125｜SettingsDialog 与 SettingsSection 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| settings-dialog.tsx | 设置弹窗总入口、section 切换。 |
| settings-section.tsx | 每个设置区块的通用布局。 |
| settings/index.ts | 导出 settings 页面组件。 |
| about-content.ts | About 页面内容。 |

```mermaid
flowchart TD
  Trigger[settings trigger] --> Dialog[SettingsDialog]
  Dialog --> SectionNav[section navigation]
  SectionNav --> Page[active settings page]
  Page --> SettingsSection
  SettingsSection --> FormControls
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
flowchart TD
  Trigger["command-palette / nav-menu"] --> Dialog["SettingsDialog open + defaultSection"]
  Dialog --> Effect["useEffect syncs activeSection"]
  Effect --> Nav["sections nav list 7 buttons"]
  Nav --> SetActive["setActiveSection id"]
  SetActive --> Render["conditional render activeSection"]
  Render --> Account["AccountSettingsPage"]
  Render --> Appearance["AppearanceSettingsPage"]
  Render --> Memory["MemorySettingsPage"]
  Render --> Tools["ToolSettingsPage"]
  Render --> Skills["SkillSettingsPage"]
  Render --> Notif["NotificationSettingsPage"]
  Render --> About["AboutSettingsPage"]
  Account --> Section["SettingsSection title + children"]
  Appearance --> Section
  Memory --> Section
  Tools --> Section
  Skills --> Section
  Notif --> Section
  About --> Section
  Section --> Scroll["ScrollArea content"]
```