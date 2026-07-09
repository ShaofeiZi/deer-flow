<title>192｜ThreadState / Reducers / Serialization Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 Docker、Provisioner、脚本和测试细模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_thread_state_reducers.py | artifacts/todos/viewed_images/promoted reducers。 |
| test_thread_state_promoted.py | deferred promoted state。 |
| test_serialization.py | runtime serialization。 |
| test_serialize_message_content.py | message content 序列化。 |
| test_converters.py | runtime converters。 |

```mermaid
flowchart TD
  ThreadState --> ReducerTests
  Messages --> SerializationTests
  Runtime --> ConverterTests
  ReducerTests --> Artifacts[merge artifacts]
  ReducerTests --> Todos[merge todos]
  ReducerTests --> Promoted[merge promoted tools]
  SerializationTests --> JSON[JSON safe output]
  ConverterTests --> APIShape[API shape]
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
flowchart TD
  Node["graph node partial state"] --> Reducer{"ThreadState reducer"}
  Reducer --> MergeTodos["merge_todos"]
  Reducer --> MergeArt["merge_artifacts"]
  Reducer --> MergeImg["merge_viewed_images"]
  Reducer --> MergeProm["merge_promoted"]
  MergeTodos --> TS["ThreadState Annotated fields"]
  MergeArt --> TS
  MergeImg --> TS
  MergeProm --> TS
  TS --> Serialize["serialize values mode"]
  Serialize --> SCV["serialize_channel_values"]
  SCV --> Strip["drop __pregel_ and __interrupt__"]
  Strip --> SLC["serialize_lc_object"]
  SLC --> MDump["model_dump / dict / str fallback"]
  MDump --> Out["JSON-safe dict"]
```