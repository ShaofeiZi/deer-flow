<title>184｜Skills / Tools / Deferred Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| test_skills\_\* | skills parser/installer/loader/custom router。 |
| test_skill_manage_tool.py | skill_manage_tool。 |
| test_tool_search.py | tool search。 |
| test_deferred\_\* | deferred tools promotion/filter。 |
| test_tool_output\_\* | 工具输出截断/预算。 |

```mermaid
flowchart TD
  UserMsg[visible user message: /skill-name task] --> Parse[parse_slash_skill_reference]
  Parse --> Resolve[resolve installed enabled available skill]
  Resolve --> Read[read SKILL.md under skills root]
  Read --> Hidden[insert hidden HumanMessage activation context]
  Hidden --> ModelCall[model call sees skill content + original user message]
  Hidden --> Audit[RunJournal middleware audit: skill_activation]
  UserMsg --> Preserve[original user content remains in state/UI]
  Deferred --> DeferredTests[promotion/filter/cross-context tests]
  ToolOutput --> OutputTests[truncate/externalize/budget tests]
  ModelCall --> CI[backend unit tests]
  DeferredTests --> CI
  OutputTests --> CI
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |
| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |
| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |
| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |

```mermaid
sequenceDiagram
    participant Build as build_deferred_tool_setup
    participant Cat as DeferredToolCatalog
    participant MW as DeferredToolFilterMiddleware
    participant Model as Model bind_tools
    participant TS as tool_search closure
    participant State as ThreadState.promoted
    participant TN as ToolNode

    Build->>Cat: collect is_mcp_tool survivors
    Cat-->>Build: catalog.hash + names
    Build-->>MW: deferred_names + catalog_hash

    Note over MW,Model: Turn 1 hidden schemas
    MW->>MW: _hidden = deferred - promoted
    MW->>Model: wrap_model_call drops deferred schemas
    Model->>TS: tool_call query select:mcp_calc
    TS->>Cat: catalog.search query
    Cat-->>TS: matched tools
    TS->>State: Command update promoted names + hash
    TS-->>Model: ToolMessage with full schemas

    Note over MW,Model: Turn 2 promoted visible
    State->>MW: merge_promoted hash-scoped
    MW->>MW: _promoted matches catalog_hash
    MW->>Model: mcp_calc now bound unsearched stays hidden

    Model->>TN: direct call to hidden deferred tool
    TN->>MW: wrap_tool_call
    MW-->>TN: error ToolMessage deferred not promoted
```