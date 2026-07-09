<title>334｜serve.sh 服务生命周期深拆</title>

<callout emoji="✅">
**本章目标：**继续拆 remaining route/content/docker/script 内部模块。
</callout>

| 模块点 | 说明 |
|-|-|
| serve.sh --dev | 开发启动。 |
| serve.sh --prod | 生产启动。 |
| --daemon | 后台运行。 |
| --stop | 停止服务。 |
| logs | gateway/frontend/nginx 日志。 |

```mermaid
flowchart TD
  MakeDev --> ServeDev
  MakeStart --> ServeProd
  ServeDev --> CheckPorts
  ServeDev --> StartGateway
  ServeDev --> StartFrontend
  ServeDev --> StartNginx
  Stop --> KillProcesses
  Daemon --> BackgroundLogs
  StartNginx --> Localhost2026
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  Args["arg parse --dev --prod --daemon --stop"]
  Args --> Action{ACTION}
  Action -->|--stop --restart| Stop["stop_all"]
  Stop --> Reclaim["_kill_repo_port 8001 3000 2026"]
  Stop --> Kill["_kill_repo_processes uvicorn next nginx"]
  Stop --> Cln["cleanup-containers.sh"]
  Action -->|--dev --prod| StopAll["stop_all then restart"]
  StopAll --> Config{"config check config.yaml"}
  Config -->|"missing"| ExitFail["exit 1 run make setup"]
  Config -->|found| Upgrade["config-upgrade.sh"]
  Upgrade --> Extras["detect_uv_extras.py"]
  Extras --> Deps["uv sync backend / pnpm install frontend"]
  Deps --> Skip{"SKIP_INSTALL"}
  Skip -->|true| Start
  Skip -->|false| Start["run_service loop"]
  Start --> GW["Gateway uvicorn app.gateway.app port 8001"]
  Start --> FE["Frontend pnpm dev or preview port 3000"]
  Start --> NX["Nginx nginx.local.conf port 2026"]
  GW --> Wait["wait-for-port.sh"]
  FE --> Wait
  NX --> Wait
  Wait --> Ready["ready localhost 2026"]
  NX --> Route["Nginx routes /api to Gateway and / to Frontend"]
```