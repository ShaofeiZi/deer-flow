<title>311｜Remaining Scripts Ops 详解</title>

<callout emoji="✅">
**本章目标：**补齐剩余 frontend/UI/misc 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| detect_thread_boundaries.py | 线程边界检测。 |
| detect_uv_extras.py | uv extras 检测。 |
| sync_labels.py | 同步 GitHub labels。 |
| tool-error-degradation-detection.sh | 工具错误降级检测。 |
| load_memory_sample.py | 加载 memory 示例。 |

```mermaid
flowchart TD
  DevOps --> DetectThreadBoundaries
  DevOps --> DetectUVExtras
  Maintainer --> SyncLabels
  QA --> ToolErrorDetection
  Demo --> LoadMemorySample
  Outputs --> Reports
  Reports --> DeveloperAction
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
  subgraph ThreadBoundaries
    TB1["detect_thread_boundaries.py"]
    TB2["BoundaryVisitor AST scan"]
    TB3["findings JSON or text"]
    TB1 --> TB2 --> TB3
  end
  subgraph UVExtras
    UV1["detect_uv_extras.py"]
    UV2["UV_EXTRAS env or config.yaml"]
    UV3["--extra flags for uv sync"]
    UV1 --> UV2 --> UV3
  end
  subgraph SyncLabels
    SL1["sync_labels.py"]
    SL2[".github/labels.yml"]
    SL3["gh label create --force"]
    SL1 --> SL2 --> SL3
  end
  subgraph ToolError
    TE1["tool-error-degradation-detection.sh"]
    TE2["build_middlewares lead and subagent"]
    TE3["ToolErrorHandlingMiddleware downgrades error and preserves outputs"]
    TE1 --> TE2 --> TE3
  end
  subgraph MemorySample
    LM1["load_memory_sample.py"]
    LM2["backend/docs/memory-settings-sample.json"]
    LM3["backend/.deer-flow/memory.json"]
    LM1 --> LM2 --> LM3
  end
```