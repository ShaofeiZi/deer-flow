<title>225｜OpenAPI / Setup / Guardrails 相关文档详解</title>

<callout emoji="✅">
**本章目标：**继续拆剩余文档/content 模块，说明用途和关联运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| API.md | OpenAPI/API 参考。 |
| SETUP.md | 后端 setup。 |
| GUARDRAILS.md | 安全策略。 |
| BLOCKING_IO_DETECTION.md | 阻塞 IO 检测。 |
| PATH_EXAMPLES.md | 路径示例。 |

```mermaid
flowchart TD
  SetupDoc --> DevSetup
  APIDoc --> OpenAPI[openapi schema]
  GuardrailsDoc --> GuardrailMiddleware
  BlockingDoc --> BlockingTests
  PathDoc --> SandboxPath
  DevSetup --> RunBackend
  OpenAPI --> FrontendClient
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
    TC["tool call request"]
    GM["GuardrailMiddleware.wrap_tool_call"]
    BR["_build_request to GuardrailRequest"]
    PV["GuardrailProvider.evaluate"]
    DEC["GuardrailDecision"]
    AL["allow=true"]
    DN["allow=false"]
    HDL["handler to tool runs"]
    DM["_build_denied_message"]
    TM["ToolMessage status=error"]
    ERR["provider raised"]
    FC["fail_closed=true"]
    FO["fail_closed=false"]
    AG["agent adapts"]

    TC --> GM
    GM --> BR
    BR --> PV
    PV --> DEC
    DEC -- AL --> HDL
    DEC -- DN --> DM
    DM --> TM
    TM --> AG
    PV -- ERR --> FC
    FC -- blocks --> DM
    ERR -- FO --> HDL
```