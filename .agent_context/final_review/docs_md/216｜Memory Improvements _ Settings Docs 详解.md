<title>216｜Memory Improvements / Settings Docs 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。
</callout>

| 文档点 | 说明 |
|-|-|
| MEMORY_IMPROVEMENTS.md | memory 改进设计。 |
| MEMORY_IMPROVEMENTS_SUMMARY.md | 改进摘要。 |
| MEMORY_SETTINGS_REVIEW.md | 设置审查。 |
| memory-settings-sample.json | 示例配置。 |
| 关联代码 | agents/memory、memory router、settings page。 |

```mermaid
flowchart TD
  MemoryDocs --> Design[improvements]
  Design --> Storage[MemoryStorage]
  Design --> Queue[MemoryQueue]
  Design --> Updater[MemoryUpdater]
  Review --> Settings[Memory settings]
  Sample --> Config[example json]
  Settings --> Frontend[Memory settings page]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
sequenceDiagram
    participant UI as memory-settings-page
    participant Hooks as core/memory/hooks
    participant API as core/memory/api
    participant Proxy as api/memory route
    participant Router as routers/memory.py
    participant Updater as memory/updater.py
    participant Storage as FileMemoryStorage
    participant File as memory.json
    UI->>Hooks: useMemory useCreate useUpdate useDelete useClear
    Hooks->>API: loadMemory createMemoryFact updateMemoryFact deleteMemoryFact clearMemory
    API->>Proxy: GET POST PATCH DELETE /api/memory/facts
    Proxy->>Router: proxy to backend /api/memory
    Router->>Updater: get_memory_data create_memory_fact update_memory_fact delete_memory_fact clear_memory_data
    Updater->>Storage: get_memory_storage save
    Storage->>File: atomic write .tmp then replace
    File-->>Storage: mtime updated
    Storage-->>Updater: saved memory dict
    Updater-->>Router: MemoryResponse
    Router-->>Proxy: 200 JSON
    Proxy-->>API: response
    API-->>Hooks: UserMemory
    Hooks->>UI: react-query setQueryData refresh
```