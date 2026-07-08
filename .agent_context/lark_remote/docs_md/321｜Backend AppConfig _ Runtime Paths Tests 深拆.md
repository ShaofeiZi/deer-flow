<title>321｜Backend AppConfig / Runtime Paths Tests 深拆</title>

<callout emoji="✅">
**本章目标：**继续拆 backend tests、frontend pages、docker/provisioner、wizard step 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_app_config_reload.py | 配置 mtime reload。 |
| test_runtime_paths.py | project root/runtime home。 |
| test_paths_user_isolation.py | 用户隔离路径。 |
| test_config_version.py | 配置版本。 |

```mermaid
flowchart TD
  ConfigFiles --> AppConfigReloadTests
  EnvVars --> RuntimePathTests
  UserId --> PathIsolationTests
  ConfigVersion --> VersionTests
  Tests --> Assertions
  Assertions --> CI
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