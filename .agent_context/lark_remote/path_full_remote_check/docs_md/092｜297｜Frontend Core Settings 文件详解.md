{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>297｜Frontend Core Settings 文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 frontend core 数据层单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| settings/local.ts | 默认设置和 local 类型。 |\n| settings/store.ts | localStorage 读写。 |\n| settings/hooks.ts | useLocalSettings/useThreadSettings。 |\n| settings/index.ts | 统一导出。 |\n\n```mermaid\nflowchart TD\n  UI --> UseLocalSettings\n  UI --> UseThreadSettings\n  UseLocalSettings --> SettingsStore\n  UseThreadSettings --> SettingsStore\n  SettingsStore --> LocalStorage\n  ThreadId --> ThreadModelOverride\n  LocalStorage --> UIState\n  ThreadModelOverride --> InputBoxContext\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**frontend settings 用 `useSyncExternalStore` 包装 localStorage，让通知、token usage、默认上下文和每个 thread 的 model override 在组件间稳定共享。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | UI 读写设置不需要 React Query 或后端请求，并且同一浏览器多标签页可通过 storage event 同步。 |\n| 代价 | SSR 环境必须返回默认值，且 thread model override 需要单独维护 `deerflow.thread-model.{threadId}`。 |\n| 重点代码 | `frontend/src/core/settings/local.ts`、`frontend/src/core/settings/store.ts`、`frontend/src/core/settings/hooks.ts`。 |\n| 阅读路径 | 先看 localStorage key 和默认值，再看 store 的 listener/snapshot，最后看 `useLocalSettings` 与 `useThreadSettings` 如何把 base settings 合并 thread override。 |\n\n```mermaid\nflowchart TD\n  LocalStorage[localStorage] --> Store[settings/store external store]\n  Store --> BaseSnapshot[getBaseSettingsSnapshot]\n  Store --> ThreadSnapshot[getThreadModelSnapshot]\n  BaseSnapshot --> useLocalSettings\n  BaseSnapshot --> useThreadSettings\n  ThreadSnapshot --> useThreadSettings\n  useThreadSettings --> Override[applyThreadModelOverride]\n  StorageEvent[window storage event] --> Store\n```",
      "document_id": "HGSzd1Ah7oHr5LxTnTUmDO0my8e",
      "revision_id": 18
    }
  }
}
