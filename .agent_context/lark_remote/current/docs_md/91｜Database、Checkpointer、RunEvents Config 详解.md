# 91｜Database、Checkpointer、RunEvents Config 详解

<callout emoji="✅">
**本章目标：**拆 database/checkpointer/run_events 相关配置。
</callout>

## 本轮源码校准补充：Database、Checkpointer、RunEvents Config

```mermaid
flowchart TD
  Lifespan[Gateway lifespan] --> DB[database engine]
  Lifespan --> Checkpointer[checkpointer]
  Lifespan --> Store[LangGraph store]
  Lifespan --> RunStore[Run store]
  Lifespan --> EventStore[Run event store]
  EventStore --> Journal[RunJournal]
  Checkpointer --> Rollback[rollback/checkpoint history]
```

| 配置 | 影响 |
|-|-|
| database | 持久化 run/thread/feedback/user 等数据的基础连接。 |
| checkpointer | LangGraph checkpoint、history、rollback 的基础。 |
| run events | run journal、message history、token/progress 记录。 |
| startup 边界 | 这些资源多在 lifespan 初始化；修改配置后通常需要重启 Gateway。 |

| 模块点 | 说明 |
|-|-|
| DatabaseConfig | 数据库 backend 和连接配置。 |
| CheckpointerConfig | LangGraph checkpoint backend 选择。 |
| RunEventsConfig | run events 存储开关和后端。 |
| StreamBridgeConfig | stream bridge backend。 |

```mermaid
flowchart TD
  Config[config yaml] --> DB[DatabaseConfig]
  Config --> CP[CheckpointerConfig]
  Config --> Events[RunEventsConfig]
  Config --> Bridge[StreamBridgeConfig]
  DB --> Engine[init_engine]
  CP --> Checkpointer[make_checkpointer]
  Events --> EventStore[make_run_event_store]
  Bridge --> StreamBridge[make_stream_bridge]
  Engine --> Repos[run feedback thread repositories]
```