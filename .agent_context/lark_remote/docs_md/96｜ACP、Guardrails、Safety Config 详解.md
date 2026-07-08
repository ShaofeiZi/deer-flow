<title>96｜ACP、Guardrails、Safety Config 详解</title>

<callout emoji="✅">
**本章目标：**补齐 ACP agent、guardrails、safety finish reason 等配置模块。
</callout>

| 模块点 | 说明 |
|-|-|
| ACPAgentConfig | 外部 ACP agent 配置。 |
| GuardrailsConfig | 工具调用 guardrail provider 配置。 |
| SafetyFinishReasonConfig | 安全终止 detector 配置。 |
| LoopDetectionConfig | 循环检测阈值和工具频率 override。 |
| SkillEvolutionConfig | agent 自演化 skill 开关。 |

```mermaid
flowchart TD
  Config[config yaml] --> ACP[ACP config]
  Config --> Guard[Guardrails config]
  Config --> Safety[Safety finish reason config]
  Config --> Loop[Loop detection config]
  Config --> Evolution[Skill evolution config]
  ACP --> ACPTool[invoke acp agent tool]
  Guard --> GuardMW[GuardrailMiddleware]
  Safety --> SafetyMW[SafetyFinishReasonMiddleware]
  Loop --> LoopMW[LoopDetectionMiddleware]
  Evolution --> Prompt[skill self evolution prompt]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块承担 agent 扩展能力，是为了把工具、知识、长期上下文或执行环境做成可组合部件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可扩展、可配置、可替换。 |
| 代价 | 代价是配置、prompt、工具 schema、外部服务任一环节出错都会影响结果。 |
| 重点代码 | 重点代码在 `backend/packages/harness/deerflow` 下对应 skills/mcp/memory/sandbox/tools/models 模块。 |
| 阅读路径 | 阅读路径：明确它给 agent 增加了什么能力，以及该能力在哪里被注入。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```