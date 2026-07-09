<title>186｜Label Sync / Triage / Container Workflow 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| label-sync.yml | 同步标签。 |
| triage.yml | issue triage 自动化。 |
| container.yaml | 容器构建。 |
| sync_labels.py | 标签同步脚本。 |

```mermaid
flowchart TD
  Schedule[scheduled/manual] --> LabelSync[label sync workflow]
  Issues[issue events] --> Triage[triage workflow]
  Push[push] --> Container[container workflow]
  LabelSync --> Script[sync_labels.py]
  Script --> Labels[GitHub labels]
  Triage --> IssueState[issue labels/comments]
  Container --> Images[container image]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
  LabelsYml[".github/labels.yml"] --> Script["scripts/sync_labels.py"]
  LabelSync["label-sync.yml push or dispatch"] --> Script
  Script --> GhCreate["gh label create --force"]
  GhCreate --> GHLabels["GitHub labels update-only"]

  TriageEvents["pull_request_target / review / issues events"] --> Triage["triage.yml"]
  Triage --> PrLabels["pr-labels job area/size/risk"]
  Triage --> Reviewing["reviewing job on maintainer review"]
  Triage --> IssueTriage["issue-triage job needs-triage"]
  PrLabels --> PrState["PR labels reconciled live"]
  Reviewing --> PrState
  IssueTriage --> IssueState["issue needs-triage label"]

  TagPush["push tag v*"] --> Container["container.yaml"]
  Container --> BackendImg["ghcr.io repo-backend backend/Dockerfile"]
  Container --> FrontendImg["ghcr.io repo-frontend frontend/Dockerfile"]
```