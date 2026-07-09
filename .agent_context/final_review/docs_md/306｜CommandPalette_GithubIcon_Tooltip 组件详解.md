<title>306｜CommandPalette、GithubIcon、Tooltip 组件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend workspace/chat/artifacts/messages 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| command-palette.tsx | 全局命令面板。 |
| github-icon.tsx | GitHub 图标。 |
| tooltip.tsx | workspace tooltip 封装。 |
| copy-button.tsx | 复制按钮也复用 workspace 交互。 |

```mermaid
flowchart TD
  KeyboardShortcut --> CommandPalette
  CommandPalette --> CommandItems
  CommandItems --> Navigation
  UI --> Tooltip
  GitHubLink --> GithubIcon
  CopyAction --> CopyButton
  CopyButton --> Clipboard
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
    actor User
    participant CopyButton as CopyButton.tsx
    participant WTooltip as workspace Tooltip
    participant ClipMod as core/clipboard.ts
    participant NavClip as navigator.clipboard
    participant DOM as execCommand fallback
    participant Toast as sonner toast
    User->>WTooltip: hover CopyButton
    WTooltip-->>User: show copyToClipboard hint
    User->>CopyButton: onClick
    CopyButton->>ClipMod: writeTextToClipboard data
    alt navigator.clipboard.writeText exists
        ClipMod->>NavClip: writeText text
        NavClip-->>ClipMod: resolve
    else fallback path
        ClipMod->>DOM: copyTextWithExecCommand text
        DOM-->>ClipMod: boolean
    end
    alt copy succeeded
        ClipMod-->>CopyButton: true
        CopyButton->>CopyButton: setCopied true for 2s
        CopyButton-->>User: swap to CheckIcon
    else copy failed
        ClipMod-->>CopyButton: false
        CopyButton->>Toast: toast.error failedToCopy
    end
```