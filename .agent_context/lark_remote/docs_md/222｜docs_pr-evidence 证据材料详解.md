<title>222｜docs/pr-evidence 证据材料详解</title>

<callout emoji="✅">
**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。
</callout>

| 文档点 | 说明 |
|-|-|
| docs/pr-evidence | PR 截图/证据目录。 |
| session-skill-manage-e2e | skill manage E2E 证据。 |
| skill-manage-e2e | 技能管理页面证据。 |
| 用途 | PR review 验证 UI/功能。 |

```mermaid
flowchart TD
  FeatureChange --> ManualOrE2E[manual or e2e verification]
  ManualOrE2E --> Screenshot[pr evidence screenshots]
  Screenshot --> PR[Pull request]
  PR --> Reviewer[reviewer checks evidence]
  Reviewer --> Decision[merge decision]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统中抽出来。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是学习和定位更聚焦。 |
| 代价 | 代价是章节数量更多，需要依赖目录维护。 |
| 重点代码 | 重点代码见本章列出的文件路径。 |
| 阅读路径 | 阅读路径：先看上游输入和下游输出，再读关键函数。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```