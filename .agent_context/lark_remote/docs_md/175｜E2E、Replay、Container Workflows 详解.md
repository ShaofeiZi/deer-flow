<title>175｜E2E、Replay、Container Workflows 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。
</callout>

| 模块点 | 说明 |
|-|-|
| e2e-tests.yml | 运行 Playwright E2E。 |
| replay-e2e.yml | 运行 replay golden 契约。 |
| container.yaml | 构建容器镜像。 |
| backend-blocking-io-tests.yml | 阻塞 IO gate。 |

```mermaid
flowchart TD
  PR --> E2E[e2e workflow]
  PR --> Replay[replay workflow]
  PR --> Container[container build]
  PR --> Blocking[blocking io]
  E2E --> Browser[Playwright browser]
  Replay --> Fixture[golden fixtures]
  Container --> Images[Docker images]
  Blocking --> Pytest[blocking io pytest]
  Browser --> Status
  Fixture --> Status
  Images --> Status
  Pytest --> Status
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统中抽出来。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是学习和定位更聚焦。 |
| 代价 | 代价是章节数量更多，需要依赖目录维护。 |
| 重点代码 | 重点代码见本章列出的文件路径。 |
| 阅读路径 | 阅读路径：先看上游输入和下游输出，再读关键函数。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```