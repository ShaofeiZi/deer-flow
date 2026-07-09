<title>295｜Frontend Core Skills 文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend core 数据层单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| skills/api.ts | load/enable/install skills。 |
| skills/hooks.ts | useSkills/useEnableSkill/useInstallSkill。 |
| skills/type.ts | Skill 类型。 |
| skills/index.ts | 统一导出。 |

```mermaid
flowchart TD
  SkillSettings --> UseSkills
  UseSkills --> LoadSkills[GET api skills]
  Switch --> EnableSkill[PUT api skills name]
  ArtifactSkill --> InstallSkill[POST api skills install]
  InstallSkill --> QueryInvalidation
  EnableSkill --> QueryInvalidation
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
flowchart TD
  SettingsPage["SkillSettingsPage"] --> UseSkills["useSkills hook"]
  UseSkills --> LoadSkills["loadSkills api.ts"]
  LoadSkills --> GetSkills["GET api/skills"]
  GetSkills -->|Skill array| UseSkills
  Switch["Switch onCheckedChange"] --> UseEnable["useEnableSkill hook"]
  UseEnable --> EnableApi["enableSkill api.ts"]
  EnableApi --> PutSkill["PUT api/skills/name"]
  PutSkill -->|onSuccess| Invalidate["invalidateQueries skills"]
  Invalidate --> UseSkills
  ArtifactDetail["artifact-file-detail"] --> InstallApi["installSkill api.ts"]
  ArtifactList["artifact-file-list"] --> InstallApi
  InstallApi --> PostInstall["POST api/skills/install"]
  PostInstall -->|InstallSkillResponse| Toast["toast success or error"]
```