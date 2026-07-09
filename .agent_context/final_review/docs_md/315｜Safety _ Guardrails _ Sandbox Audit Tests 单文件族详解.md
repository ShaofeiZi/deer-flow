<title>315｜Safety / Guardrails / Sandbox Audit Tests 单文件族详解</title>

<callout emoji="✅">
**本章目标：**继续拆更细 backend/frontend/skill scripts 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_guardrail_middleware.py | guardrail。 |
| test_safety_finish_reason_middleware.py | 安全终止。 |
| test_safety_termination_detectors.py | detectors。 |
| test_sandbox_audit_middleware.py | sandbox audit。 |
| test_sandbox_tools_security.py | sandbox tools security。 |

```mermaid
flowchart TD
  ToolCall --> GuardrailTests
  AIMessage --> SafetyTests
  ProviderMetadata --> DetectorTests
  BashCommand --> SandboxAuditTests
  FilePath --> SandboxSecurityTests
  Tests --> SafetyGate
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
  AIMsg["AIMessage from model"] --> AfterModel["SafetyFinishReasonMiddleware after_model"]
  AfterModel --> Det["OpenAICompatible / AnthropicRefusal / GeminiSafety detectors"]
  Det --> Hit{"termination hit"}
  Hit -- yes --> Strip["strip tool_calls, stamp safety_termination, emit SSE and journal"]
  Strip --> NoRun["return patched message, tools not run"]
  Hit -- no --> Dispatch["tool_calls dispatched"]
  Dispatch --> GR["GuardrailMiddleware.wrap_tool_call"]
  GR --> Eval["provider.evaluate GuardrailRequest"]
  Eval --> Dec{"allow"}
  Dec -- no --> Deny["error ToolMessage oap.denied"]
  Dec -- yes --> SA["SandboxAuditMiddleware.wrap_tool_call bash only"]
  SA --> Blk{"_classify_command verdict"}
  Blk -- block --> BlkMsg["block ToolMessage, handler skipped"]
  Blk -- warn --> RunW["handler runs, warning appended"]
  Blk -- pass --> RunOK["handler runs, bash executes"]
```