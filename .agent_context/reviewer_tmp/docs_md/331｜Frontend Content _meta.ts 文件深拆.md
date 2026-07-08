<title>331｜Frontend Content _meta.ts 文件深拆</title>

<callout emoji="✅">
**本章目标：**继续拆 remaining route/content/docker/script 内部模块。
</callout>

| 模块点 | 说明 |
|-|-|
| \_meta.ts root | 语言根目录元数据。 |
| application/\_meta.ts | 应用文档目录。 |
| harness/\_meta.ts | harness 文档目录。 |
| reference/\_meta.ts | 参考文档目录。 |
| tutorials/\_meta.ts | 教程目录。 |
| posts/\_meta.ts | 博客元数据。 |

```mermaid
flowchart TD
  ContentDirs --> RootMeta
  RootMeta --> PageMap
  ApplicationMeta --> PageMap
  HarnessMeta --> PageMap
  ReferenceMeta --> PageMap
  TutorialsMeta --> PageMap
  PostsMeta --> BlogIndex
  PageMap --> NextraSidebar
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 好处是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 坏处是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```