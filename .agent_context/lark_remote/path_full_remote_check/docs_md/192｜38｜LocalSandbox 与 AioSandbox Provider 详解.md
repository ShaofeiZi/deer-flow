{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>38｜LocalSandbox 与 AioSandbox Provider 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清本地 sandbox 与容器化 AioSandbox provider 的职责差异和路径映射。\n</callout>\n\n| Provider | 职责 | 适用场景 |\n|-|-|-|\n| `LocalSandboxProvider` | 使用宿主机文件系统路径映射，bash 默认禁用 | 本地开发、可信环境。 |\n| `AioSandboxProvider` | 容器/远程 provisioner sandbox，支持 acquire/reuse/release | 隔离要求更高的开发或生产。 |\n| `docker/provisioner` | 在 Kubernetes 中创建 sandbox Pod/Service | 集群部署。 |\n\n```mermaid\nflowchart TD\n  Config[sandbox.use] --> Provider{provider type}\n  Provider --> Local[LocalSandboxProvider]\n  Provider --> Aio[AioSandboxProvider]\n  Local --> Mapping[host path mappings]\n  Mapping --> LocalSandbox[LocalSandbox]\n  Aio --> Backend{backend}\n  Backend --> Docker[local docker backend]\n  Backend --> Remote[remote provisioner]\n  Remote --> Pod[Kubernetes pod]\n  Docker --> Container[sandbox container]\n  Container --> SandboxAPI[execute/read/write/list]\n  Pod --> SandboxAPI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这些模块负责扩展 agent 能力：skill 提供方法论，MCP 提供外部工具，memory 提供长期上下文。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是能力可扩展、可配置、可跨会话复用。 |\n| 代价 | 代价是 prompt、工具、记忆三者都会影响模型行为，问题定位需要分层排查。 |\n| 重点代码 | 重点代码在 `backend/packages/harness/deerflow/skills`、`mcp`、`agents/memory`。 |\n| 阅读路径 | 阅读路径：把 skill 当说明书，MCP 当工具注册表，memory 当上下文注入源。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "DujDdwq1uoWq1lxzFJ6m3ACSyYc",
      "revision_id": 15
    }
  }
}
