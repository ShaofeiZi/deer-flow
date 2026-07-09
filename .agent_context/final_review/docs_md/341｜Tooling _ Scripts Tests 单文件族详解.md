<title>341｜Tooling / Scripts Tests 单文件族详解</title>

<callout emoji="✅">
**本章目标：**补齐 remaining scripts/tests/routes/package docs 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_check_script.py | check.py。 |
| test_detect_blocking_io_static.py | blocking IO script。 |
| test_detect_thread_boundaries.py | thread boundary script。 |
| test_detect_uv_extras.py | uv extras script。 |
| test_dev_entrypoint.py | docker dev entrypoint。 |

```mermaid
flowchart TD
  Scripts --> ScriptTests
  CheckScript --> TestCheck
  BlockingScript --> TestBlockingDetect
  ThreadScript --> TestThreadDetect
  UVScript --> TestUV
  DevEntrypoint --> TestEntrypoint
  ScriptTests --> CI
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
flowchart LR
  Tchk["test_check_script.py"] -->|"importlib.spec"| Chk["scripts/check.py"]
  Tuv["test_detect_uv_extras.py"] -->|"importlib.spec"| Uv["scripts/detect_uv_extras.py"]
  Chk --> ChkFn["find_pnpm_command"]
  Uv --> UvFn["resolve_extras parse_env_extras format_flags"]
  Tblk["test_detect_blocking_io_static.py"] -->|"from support.detectors"| Blk["support/detectors/blocking_io_static.py"]
  Tthr["test_detect_thread_boundaries.py"] -->|"from support.detectors"| Thr["support/detectors/thread_boundaries.py"]
  Blk --> BlkFn["scan_file main --format json"]
  Thr --> ThrFn["scan_file main --min-severity"]
  Tdev["test_dev_entrypoint.py"] -->|"subprocess sh"| Dev["docker/dev-entrypoint.sh"]
  Dev --> DevFn["--print-extras UV_EXTRAS --extra X"]
```