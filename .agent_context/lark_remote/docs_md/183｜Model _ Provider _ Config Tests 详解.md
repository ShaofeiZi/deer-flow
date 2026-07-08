<title>183｜Model / Provider / Config Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| test_model_factory.py | 模型工厂。 |
| test_model_config.py | 模型配置。 |
| test_patched\_\*.py | provider patch。 |
| test_claude_provider\_\* | Claude provider。 |
| test_config_version/app_config_reload | 配置版本和热加载。 |

```mermaid
flowchart TD
  ConfigFiles --> ConfigTests
  ModelFactory --> FactoryTests
  Providers --> ProviderTests
  Claude --> ClaudeTests
  ConfigTests --> Validation[pydantic validation]
  FactoryTests --> ClassResolve[class resolve]
  ProviderTests --> Compat[provider compatibility]
  Validation --> CI
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