<title>220｜Apple Container / Auth Docker Gap Docs 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。
</callout>

| 文档点 | 说明 |
|-|-|
| APPLE_CONTAINER.md | Apple container 相关说明。 |
| AUTH_TEST_DOCKER_GAP.md | Auth 测试与 Docker 缺口。 |
| AUTH_TEST_PLAN.md | Auth 测试计划。 |
| 关联 | Docker、auth router、CI。 |

```mermaid
flowchart TD
  AppleDoc --> ContainerContext[Apple container notes]
  AuthPlan --> AuthTests
  DockerGap --> Gap[known docker test gaps]
  Gap --> FutureTests
  AuthTests --> CI
  ContainerContext --> DockerDocs
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |
| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |
| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |
| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |

```mermaid
flowchart TD
  Deploy["scripts/deploy.sh"] --> Compose["docker-compose.yaml"]
  Compose --> GW["gateway worker"]
  Compose --> Nginx["nginx port 2026"]
  Compose --> Vol["DEER_FLOW_HOME volume"]
  GW --> Token["INTERNAL_AUTH_TOKEN"]
  Browser["browser access_token cookie"] --> Nginx
  Channel["channels/manager.py"] -->|"X-DeerFlow-Internal-Token"| AuthMW["AuthMiddleware"]
  Nginx -->|"proxy /api"| AuthMW
  AuthMW -->|"public path"| AuthRouter["auth router login-local"]
  AuthMW -->|"JWT validate"| Routes["protected routes"]
  GW --> Sandbox["LocalContainerBackend detect_runtime"]
  Sandbox -->|"Darwin has container CLI"| Apple["Apple Container"]
  Sandbox -->|"fallback"| DockerRT["Docker runtime"]
```