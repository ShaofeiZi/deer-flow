<title>177｜serve.sh、docker.sh、deploy.sh 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。
</callout>

| 模块点 | 说明 |
|-|-|
| serve.sh | 本地 dev/prod 启动、停止、daemon。 |
| docker.sh | Docker 开发环境 init/start/stop/logs。 |
| deploy.sh | 生产 Docker build/start/down。 |
| wait-for-port.sh | 等待服务端口。 |
| start-daemon.sh | 后台启动辅助。 |

```mermaid
flowchart TD
  MakeDev[make dev] --> Serve[serve sh]
  Serve --> CheckPorts[wait for ports]
  Serve --> Gateway[Gateway process]
  Serve --> Frontend[Frontend process]
  Serve --> Nginx[Nginx process]
  MakeDocker[docker-start] --> Docker[docker sh]
  Docker --> ComposeDev[docker compose dev]
  MakeUp[make up] --> Deploy[deploy sh]
  Deploy --> ComposeProd[docker compose production]
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