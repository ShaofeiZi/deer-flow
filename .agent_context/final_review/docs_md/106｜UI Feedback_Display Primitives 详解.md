<title>106｜UI Feedback/Display Primitives 详解</title>

<callout emoji="✅">
**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| alert.tsx | 告警/提示块。 |
| badge.tsx | 状态标签。 |
| skeleton.tsx | 加载骨架屏。 |
| progress.tsx | 进度条。 |
| tooltip.tsx | 悬浮提示。 |
| sonner.tsx | toast provider。 |

```mermaid
flowchart TD
  State[UI state] --> Alert
  State --> Badge
  Loading --> Skeleton
  ProgressState --> Progress
  Hover --> Tooltip
  ToastEvent --> Sonner
  Alert --> Workspace
  Badge --> Cards
  Skeleton --> LoadingViews
  Sonner --> Toaster
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
  Route["app/workspace route"] --> WC["WorkspaceContent"]
  WC --> QCP["QueryClientProvider"]
  QCP --> Toaster["ui/sonner Toaster mounted once"]
  WC --> ML["message-list"]
  ML -- "loading" --> MLSkel["MessageListSkeleton"]
  MLSkel --> Skel["ui/skeleton"]
  Hook["core/threads/hooks.ts stream"] -- "llm_retry event" --> ToastCall["toast message"]
  Hook -- "onError" --> ToastErr["toast.error"]
  ToastCall --> Toaster
  ToastErr --> Toaster
  ML -- "ai message" --> TokenUsage["message-token-usage"]
  TokenUsage --> Badge["ui/badge token counts"]
  CTX["ai-elements/context"] --> Prog["ui/progress"]
  Tip["workspace/tooltip"] --> UiTip["ui/tooltip"]
  AgentsPage["workspace/agents/new page"] --> Alert["ui/alert"]
```