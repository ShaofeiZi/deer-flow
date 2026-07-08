# 98｜memory_config、sandbox_config、skills_config 单文件详解

<callout emoji="✅">
**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。
</callout>

## 本轮源码校准补充：memory_config、sandbox_config、skills_config

| 文件 | 学习重点 |
|-|-|
| `memory_config.py` | memory 开关、存储、token counting、用户/agent 作用域。 |
| `sandbox_config.py` | provider、路径挂载、bash/file-write、安全边界。 |
| `skills_config.py` | public/custom skill 路径、启停、解析和 prompt 注入。 |

```mermaid
flowchart LR
  Config[config files] --> Runtime[app config]
  Runtime --> Memory[Memory middleware]
  Runtime --> Sandbox[Sandbox provider]
  Runtime --> Skills[Skill storage]
  Skills --> Lead[lead_agent prompt/tools]
  Memory --> Lead
  Sandbox --> Tools[tool execution]
```

| 模块点 | 说明 |
|-|-|
| memory_config | memory 开关、注入、存储路径、token 计数。 |
| sandbox_config | sandbox provider、mounts、allow_host_bash。 |
| skills_config | skills path、container_path、候选路径。 |
| 运行影响 | 分别影响 Dynamic/Memory middleware、SandboxProvider、SkillStorage。 |

```mermaid
flowchart TD
  ConfigYaml --> MemoryConfig
  ConfigYaml --> SandboxConfig
  ConfigYaml --> SkillsConfig
  MemoryConfig --> DynamicContext
  MemoryConfig --> MemoryMiddleware
  SandboxConfig --> SandboxProvider
  SandboxConfig --> SandboxTools
  SkillsConfig --> SkillStorage
  SkillsConfig --> SkillActivation
```