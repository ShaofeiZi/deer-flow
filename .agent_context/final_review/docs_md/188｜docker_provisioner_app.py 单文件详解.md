<title>188｜docker/provisioner/app.py 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 Docker、Provisioner、脚本和测试细模块。
</callout>

| 模块点 | 说明 |
|-|-|
| FastAPI provisioner | 为远程 sandbox 创建 Pod/Service。 |
| Kubernetes client | 读取 kubeconfig / in-cluster config。 |
| PVC/volume | 为 sandbox 注入持久卷或挂载。 |
| API | 创建、查询、释放 sandbox 资源。 |

```mermaid
flowchart TD
  Gateway[AioSandbox remote backend] --> Provisioner[provisioner FastAPI]
  Provisioner --> Kube[Kubernetes API]
  Kube --> Pod[Sandbox Pod]
  Kube --> Service[NodePort Service]
  Pod --> Ready[health ready]
  Ready --> Gateway
  Gateway --> AioSandbox[AioSandbox URL]
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
sequenceDiagram
    participant Caller as remote_backend
    participant App as FastAPI app
    participant CS as create_sandbox
    participant K8s as core_v1 CoreV1Api
    participant Pod as sandbox Pod
    participant Svc as NodePort Service

    Note over App: lifespan starts
    App->>K8s: _wait_for_kubeconfig
    App->>K8s: _init_k8s_client
    App->>K8s: _ensure_namespace

    Caller->>App: POST /api/sandboxes
    App->>CS: CreateSandboxRequest
    CS->>K8s: _get_node_port sandbox_id
    alt node_port exists
        K8s-->>CS: existing port
        CS->>K8s: _get_pod_phase
        CS-->>Caller: SandboxResponse idempotent
    else not exists
        CS->>K8s: create_namespaced_pod _build_pod
        K8s->>Pod: sandbox-id Pod
        CS->>K8s: create_namespaced_service _build_service
        alt Service 409 or error
            CS->>K8s: delete_namespaced_pod rollback
            CS-->>Caller: HTTPException 500
        else Service created
            K8s->>Svc: NodePort selector sandbox-id
            loop up to 20 times
                CS->>K8s: _get_node_port poll
                K8s-->>CS: node_port
            end
            CS->>K8s: _get_pod_phase
            CS-->>Caller: SandboxResponse sandbox_url NODE_HOST port
        end
    end
```