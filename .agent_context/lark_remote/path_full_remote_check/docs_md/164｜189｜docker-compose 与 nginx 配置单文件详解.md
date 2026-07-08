{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 189｜docker-compose 与 nginx 配置单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 Docker、Provisioner、脚本和测试细模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| docker-compose-dev.yaml | 开发 compose，源码挂载和热更新。 |\n| docker-compose.yaml | 生产 compose。 |\n| nginx.local.conf | 本地 nginx 反代。 |\n| nginx.conf | 生产 nginx 反代。 |\n| dev-entrypoint.sh | 开发容器入口。 |\n\n## 补充：Docker Compose 简化运行图\n\n```mermaid\nflowchart TD\n  A[docker compose dev] --> B[Gateway]\n  A --> C[Frontend]\n  A --> D[Nginx local]\n  E[docker compose prod] --> F[Gateway prod]\n  E --> G[Frontend prod]\n  E --> H[Nginx prod]\n  D --> I[api langgraph rewrite]\n  H --> I\n  I --> B\n  I --> F\n```",
      "document_id": "HziodLMsjoqwiJxH48NmgqHKyXf",
      "revision_id": 19
    }
  }
}
