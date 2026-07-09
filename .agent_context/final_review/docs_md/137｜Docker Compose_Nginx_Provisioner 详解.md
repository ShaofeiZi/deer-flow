<title>137｜Docker Compose、Nginx、Provisioner 详解</title>

<callout emoji="✅">
**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| docker-compose-dev.yaml | Docker 开发环境。 |
| docker-compose.yaml | 生产容器编排。 |
| nginx.local.conf/nginx.conf | 统一入口和 /api/langgraph rewrite。 |
| provisioner/app.py | Kubernetes sandbox provisioner。 |
| dev-entrypoint.sh | 容器开发入口。 |

## 补充：Docker 与 Nginx 简化运行图

```mermaid
flowchart TD
  A[Docker Compose] --> B[Gateway container]
  A --> C[Frontend container]
  A --> D[Nginx container]
  D --> E[api langgraph rewrite]
  E --> B
  D --> C
  B --> F[Sandbox mode]
  F --> G[Local Docker sandbox]
  F --> H[Provisioner]
  H --> I[Kubernetes Pod]
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
sequenceDiagram
    participant BE as Backend gateway
    participant NX as nginx 2026
    participant PR as provisioner app.py 8002
    participant K8s as K8s CoreV1Api
    participant SB as sandbox Pod NodePort

    BE->>NX: POST /api/sandboxes
    NX->>PR: location /api/sandboxes proxy_pass provisioner 8002
    PR->>K8s: read_namespaced_service _get_node_port
    alt node_port already exists
        PR-->>BE: SandboxResponse existing url
    else new sandbox
        PR->>K8s: create_namespaced_pod _build_pod
        PR->>K8s: create_namespaced_service _build_service NodePort
        loop poll up to 20 times
            PR->>K8s: read_namespaced_service node_port
        end
        PR-->>BE: SandboxResponse sandbox_url
    end
    BE->>SB: direct http NODE_HOST NodePort
```