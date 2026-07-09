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
**设计目的：**该文档说明前端 UI primitive、workspace 组件或页面模块的职责、状态来源和渲染分支。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 组件边界清晰后，UI 问题可按 props/state/hook/route 快速定位。 |
| 代价 | 一次交互常跨页面、hook、context 和展示组件，需要按数据流追踪。 |
| 重点代码 | 标题对应的 `frontend/src/app/`、`frontend/src/components/` 或 `frontend/src/core/` 文件。 |
| 阅读路径 | 先看组件输入输出，再看状态来源，最后看事件回调如何改变 UI。 |

```mermaid
flowchart TD
  Env["DEER_FLOW_CONFIG_PATH"] --> AppConfigResolve["AppConfig.resolve_config_path"]
  ProjRoot["project_root cwd or env"] --> AppConfigResolve
  Legacy["legacy backend/repo root"] --> AppConfigResolve
  AppConfigResolve --> FromFile["AppConfig.from_file"]
  FromFile --> CheckVer["_check_config_version"]
  CheckVer --> Warn["logger warning if outdated"]
  FromFile --> ApplySingleton["_apply_singleton_configs"]
  ApplySingleton --> LoadTitle["load_title_config"]
  ApplySingleton --> LoadMemory["load_memory_config"]
  ApplySingleton --> LoadGuard["load_guardrails_config"]
  ApplySingleton --> LoadCheck["load_checkpointer_config"]
  LoadCheck --> ResetRuntime["reset_checkpointer reset_store"]
  Caller["get_app_config"] --> Ctx["_current_app_config ContextVar"]
  Caller --> Mtime["_app_config_path mtime check"]
  Mtime --> Reload["_load_and_cache_app_config"]
  Reload --> FromFile
```