{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 175｜E2E、Replay、Container Workflows 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| e2e-tests.yml | 运行 Playwright E2E。 |\n| replay-e2e.yml | 运行 replay golden 契约。 |\n| container.yaml | 构建容器镜像。 |\n| backend-blocking-io-tests.yml | 阻塞 IO gate。 |\n\n```mermaid\nflowchart TD\n  PR --> E2E[e2e workflow]\n  PR --> Replay[replay workflow]\n  PR --> Container[container build]\n  PR --> Blocking[blocking io]\n  E2E --> Browser[Playwright browser]\n  Replay --> Fixture[golden fixtures]\n  Container --> Images[Docker images]\n  Blocking --> Pytest[blocking io pytest]\n  Browser --> Status\n  Fixture --> Status\n  Images --> Status\n  Pytest --> Status\n```",
      "document_id": "VBOSdCNrtomPTMxUnJgmWAuxyWc",
      "revision_id": 18
    }
  }
}
