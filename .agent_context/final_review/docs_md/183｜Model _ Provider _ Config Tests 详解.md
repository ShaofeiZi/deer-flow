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
**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |
| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |
| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |
| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |

```mermaid
flowchart TD
  Entry["create_chat_model name thinking_enabled"]
  Entry --> Resolve["get_model_config name"]
  Resolve --> Found{"found"}
  Found -->|"no"| Err["raise ValueError"]
  Found -->|"yes"| Class["resolve_class use BaseChatModel"]
  Class --> Dump["model_dump exclude wte wtd thinking"]
  Dump --> On{"thinking_enabled"}
  On -->|"True"| Guard{"supports_thinking"}
  Guard -->|"False"| ErrThink["raise ValueError"]
  Guard -->|"True"| ApplyOn["merge effective_wte"]
  On -->|"False"| Fmt{"disable format"}
  Fmt --> WTD["when_thinking_disabled precedence"]
  Fmt --> OAI["extra_body thinking disabled"]
  Fmt --> ANTH["thinking type disabled"]
  Fmt --> VLLM["chat_template_kwargs false"]
  ApplyOn --> Build["model_class kwargs plus stream defaults"]
  WTD --> Build
  OAI --> Build
  ANTH --> Build
  VLLM --> Build
  Build --> Done["return instance with tracing"]
```