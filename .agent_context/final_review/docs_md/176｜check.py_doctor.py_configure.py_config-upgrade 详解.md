<title>176｜check.py、doctor.py、configure.py、config-upgrade 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。
</callout>

| 模块点 | 说明 |
|-|-|
| check.py | 检查 Python/Node/pnpm/uv/nginx 等依赖。 |
| doctor.py | 诊断配置、模型、环境问题。 |
| configure.py | 生成 config.yaml。 |
| config-upgrade.sh | 合并新配置字段。 |

```mermaid
flowchart TD
  User --> MakeCheck[make check]
  MakeCheck --> CheckPy[check.py]
  User --> MakeDoctor[make doctor]
  MakeDoctor --> Doctor[doctor.py]
  User --> MakeConfig[make config]
  MakeConfig --> Configure[configure.py]
  User --> Upgrade[make config-upgrade]
  Upgrade --> Merge[config-upgrade sh]
  Configure --> Config[config yaml]
  Merge --> Config
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
  Dr["doctor.py check_config_version"] --> Warn["warn user_ver below example_ver"]
  Warn --> Sug["suggest make config-upgrade"]
  Sug --> Up["config-upgrade.sh"]
  Up --> Resolve["resolve CONFIG path"]
  Resolve --> Exists{"config.yaml exists?"}
  Exists -- no --> Copy["cp config.example.yaml"]
  Copy --> Done1["exit created"]
  Exists -- yes --> Cmp{"versions equal or newer?"}
  Cmp -- yes --> Uptd["exit already up to date"]
  Cmp -- no --> Mig["apply MIGRATIONS replacements"]
  Mig --> Merge["recursive merge missing fields"]
  Merge --> Bump["set config_version example_version"]
  Bump --> Bak["backup config.yaml.bak"]
  Bak --> Write["write config.yaml"]
```