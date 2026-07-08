<title>128｜Artifacts Context、Trigger、List、Detail 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend 业务模块，说明职责、数据源和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| context.tsx | ArtifactsProvider 状态管理。 |
| artifact-trigger.tsx | 打开 artifacts 面板。 |
| artifact-file-list.tsx | 文件列表、选择、下载、install skill。 |
| artifact-file-detail.tsx | 详情预览、代码、下载。 |

```mermaid
flowchart TD
  ThreadValues[thread.values.artifacts] --> Context[ArtifactsProvider]
  Context --> Trigger[ArtifactTrigger]
  Trigger --> Open[set open true]
  Context --> List[ArtifactFileList]
  List --> Select[select filepath]
  Select --> Detail[ArtifactFileDetail]
  Detail --> Load[useArtifactContent]
  Detail --> Preview[code preview download install]
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
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```