{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 332｜Docker Provisioner README/Dockerfile 深拆\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 remaining route/content/docker/script 内部模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| docker/provisioner/README.md | provisioner 使用说明。 |\n| Dockerfile | provisioner 镜像构建。 |\n| app.py | FastAPI 服务。 |\n| docker-compose | 如何接入 provisioner。 |\n| K8s runtime | Pod/Service 创建。 |\n\n```mermaid\nflowchart TD\n  README --> Usage\n  Dockerfile --> Image\n  Image --> ProvisionerContainer\n  ProvisionerContainer --> AppPy\n  GatewayConfig --> ProvisionerURL\n  ProvisionerURL --> AppPy\n  AppPy --> Kubernetes\n```",
      "document_id": "PoXqdni5MoeZV8xfMecm247oyDe",
      "revision_id": 18
    }
  }
}
