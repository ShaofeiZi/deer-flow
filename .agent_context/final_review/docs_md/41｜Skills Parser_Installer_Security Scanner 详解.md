<title>41｜Skills Parser、Installer、Security Scanner 详解</title>

<callout emoji="✅">
**本章目标：**讲清 skill 从 SKILL.md 解析、压缩包安装、安全扫描到 allowed_tools 过滤的完整链路。
</callout>

| 文件 | 职责 |
|-|-|
| `skills/parser.py` | 解析 frontmatter、description、allowed_tools。 |
| `skills/installer.py` | 安全解压 .skill、扫描、移动到目标目录。 |
| `skills/security_scanner.py` | 用 LLM/规则扫描 skill 内容风险。 |
| `skills/tool_policy.py` | 根据 skill allowed_tools 过滤可用工具。 |
| `skills/slash.py` | 解析 /skill-name 显式激活。 |

## 补充：Skills 安装与激活简化运行图

```mermaid
flowchart TD
  A[SKILL md] --> B[parse frontmatter]
  B --> C[Skill object]
  D[skill archive] --> E[safe extract]
  E --> F[security scan]
  F --> G[install to skills custom]
  C --> H[allowed tools policy]
  I[all tools] --> H
  H --> J[filtered tools]
  K[user slash skill] --> L[resolve skill]
  L --> M[SkillActivationMiddleware]
  M --> N[inject full SKILL instructions]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**Skills parser、installer 和 security scanner 把 `SKILL.md` 从普通 Markdown 变成可启停、可校验、可注入 prompt 的 agent 能力单元。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | public/custom skills 能用同一套 metadata、启停状态和安全检查进入 lead agent。 |
| 代价 | skill 内容、frontmatter、allowed tools、安装来源和 prompt cache 任一处出错都会影响激活效果。 |
| 重点代码 | `backend/packages/harness/deerflow/skills/`、`backend/app/gateway/routers/skills.py`、`frontend/src/core/skills/`。 |
| 阅读路径 | 先看 parser 如何读 `SKILL.md`，再看 storage/installer 如何管理 custom skill，最后看 router 和 middleware 如何启用。 |

```mermaid
sequenceDiagram
  participant FE as frontend installSkill
  participant RT as router install_skill
  participant ST as LocalSkillStorage
  participant EX as installer safe_extract
  participant SC as security_scanner
  participant FS as filesystem custom dir

  FE->>RT: POST /api/skills/install
  RT->>RT: resolve_thread_virtual_path
  RT->>ST: ainstall_skill_from_archive
  ST->>EX: safe_extract_skill_archive
  EX->>EX: reject unsafe paths and symlinks
  EX-->>ST: skill_dir
  ST->>ST: _validate_skill_frontmatter
  ST->>SC: _scan_skill_archive_contents_or_raise
  SC->>SC: LLM scan_skill_content allow warn block
  alt decision block
    SC-->>ST: SkillSecurityScanError
    RT-->>FE: HTTP 400 blocked
  else allow or warn
    ST->>FS: _move_staged_skill_into_reserved_target
    ST-->>RT: success skill_name
    RT->>RT: refresh_skills_system_prompt_cache_async
    RT-->>FE: HTTP 200 SkillInstallResponse
  end
```
