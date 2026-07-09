<title>141｜Development/Deploy Public Skills 详解</title>

<callout emoji="✅">
**本章目标：**把 public skills 按能力组拆开，说明触发场景、工作流和运行逻辑。
</callout>

| Skill | 职责 |
|-|-|
| `frontend-design` | 前端设计与页面实现。 |
| `web-design-guidelines` | Web 设计指南。 |
| `code-documentation` | 代码文档化。 |
| `vercel-deploy-claimable` | Vercel 部署并生成可认领链接。 |
| `claude-to-deerflow` | Claude 到 DeerFlow 迁移/状态脚本。 |

```mermaid
flowchart TD
  User[User task] --> Match[Skill relevance or slash command]
  Match --> Load[read SKILL md]
  Load --> Plan[development and deploy workflow]
  Plan --> Tools[use allowed tools or scripts]
  Tools --> Output[deliver artifact or answer]
  Output --> Agent[agent continues conversation]
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
  subgraph FD["frontend-design"]
    FD1["frontend request"] --> FD2["SKILL.md aesthetic direction"] --> FD3["index.html + Deerflow badge"]
  end
  subgraph WD["web-design-guidelines"]
    WD1["UI file arg"] --> WD2["WebFetch vercel-labs rules"] --> WD3["rule findings"]
  end
  subgraph CD["code-documentation"]
    CD1["codebase"] --> CD2["analysis phases"] --> CD3["README/API/architecture docs"]
  end
  subgraph VD["vercel-deploy-claimable"]
    VD1["project dir"] --> VD2["deploy.sh detect_framework"] --> VD3["previewUrl + claimUrl"]
  end
  subgraph CT["claude-to-deerflow"]
    CT1["message arg"] --> CT2["chat.sh health and /runs/stream"] --> CT3["final AI response"]
  end
```