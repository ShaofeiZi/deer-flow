<title>163｜vercel-deploy-claimable Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**Vercel 部署并生成可认领链接。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `vercel-deploy-claimable` |
| 路径 | `skills/public/vercel-deploy-claimable/SKILL.md` |
| 类型 | deploy |
| 触发方式 | 任务匹配或显式 `/vercel-deploy-claimable` |

```mermaid
flowchart TD
  User[User task] --> Match[match vercel-deploy-claimable]
  Match --> Read[read skills public vercel-deploy-claimable SKILL md]
  Read --> Workflow[deploy workflow]
  Workflow --> Scripts[use bundled scripts if present]
  Scripts --> Output[deliver artifact or answer]
  Output --> Agent[agent continues]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档说明一个 public skill 或 skill 分类的目标、触发条件、执行链路和维护边界，方便新同学理解 DeerFlow 的可扩展能力。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | skill 能力被文档化后，使用者能快速判断何时触发、读哪些文件、如何验证输出。 |
| 代价 | skill 文档容易和实际 `SKILL.md` 漂移，需要定期回到源码和示例验证。 |
| 重点代码 | 对应 `skills/public/.../SKILL.md`、相关 `references/`、`templates/`、`scripts/`。 |
| 阅读路径 | 先读 skill frontmatter 和触发场景，再读正文 workflow，最后检查 references/templates/scripts 是否支撑描述。 |

```mermaid
flowchart TD
  Arg["deploy.sh INPUT_PATH arg"] --> Check["is .tgz or directory"]
  Check -->|tgz file| UseTar["use file as TARBALL"]
  Check -->|directory| Pkg["read package.json"]
  Pkg --> Detect["detect_framework has_dep checks"]
  Pkg -->|no package.json| Rename["rename single html to index.html"]
  Detect --> FW["set FRAMEWORK name"]
  Rename --> FW
  FW --> Tar["tar -czf exclude node_modules and git"]
  UseTar --> Curl
  Tar --> Curl["curl POST to DEPLOY_ENDPOINT"]
  Curl --> Resp["RESPONSE JSON body"]
  Resp --> Err["check error key"]
  Err -->|yes| Fail["exit 1 print ERROR_MSG"]
  Err -->|no| Parse["grep previewUrl and claimUrl"]
  Parse --> Out["stdout JSON plus stderr URLs"]
```