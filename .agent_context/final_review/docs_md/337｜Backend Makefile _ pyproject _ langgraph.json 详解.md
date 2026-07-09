<title>337｜Backend Makefile / pyproject / langgraph.json 详解</title>

<callout emoji="✅">
**本章目标：**补齐 remaining scripts/tests/routes/package docs 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| backend/Makefile | 后端 test/lint/dev 命令。 |
| backend/pyproject.toml | 后端依赖和 dev deps。 |
| packages/harness/pyproject.toml | harness 包。 |
| backend/langgraph.json | LangGraph graph registry。 |

```mermaid
flowchart TD
  BackendMake --> Dev[Test Lint Dev]
  Pyproject --> UV[uv sync]
  HarnessPyproject --> Package[deerflow harness]
  LanggraphJson --> GraphRegistry
  GraphRegistry --> make_lead_agent
  UV --> BackendRuntime
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
  Makefile["backend/Makefile"] -->|"make dev / make gateway"| Uvicorn["uvicorn app.gateway.app:app"]
  Uvicorn --> App["app/gateway/app.py FastAPI"]
  App -->|"lifespan"| Runtime["langgraph_runtime in deps.py"]
  App --> LanggraphJson["backend/langgraph.json"]
  LanggraphJson -->|"graphs.lead_agent"| MLAgent["deerflow.agents:make_lead_agent"]
  LanggraphJson -->|"auth.path"| LGAuth["app/gateway/langgraph_auth.py:auth"]
  LanggraphJson -->|"checkpointer.path"| AsyncProvider["runtime/checkpointer/async_provider.py:make_checkpointer"]
  RootPy["backend/pyproject.toml"] -->|"depends on deerflow-harness"| HarnessPkg["packages/harness/pyproject.toml"]
  RootPy -->|"tool.uv.workspace members"| HarnessPkg
  HarnessPkg -->|"hatchling packages=deerflow"| MLAgent
  MLAgent -->|"create_agent + ThreadState"| LeadAgent["lead_agent/agent.py build_middlewares"]
```