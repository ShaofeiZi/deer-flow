<title>219｜Backend RFC Docs 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。
</callout>

| 文档点 | 说明 |
|-|-|
| rfc-create-deerflow-agent.md | 创建 DeerFlow agent RFC。 |
| rfc-grep-glob-tools.md | grep/glob tools RFC。 |
| rfc-extract-shared-modules.md | 共享模块抽取 RFC。 |
| 关联代码 | agents factory、sandbox search tools、shared modules。 |

```mermaid
flowchart TD
  RFC[proposal] --> Design[design decision]
  Design --> Implementation[code implementation]
  Implementation --> Tests[tests]
  RFC1[create agent] --> AgentFactory
  RFC2[grep glob] --> SandboxSearch
  RFC3[shared modules] --> Refactor
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 好处是前后端契约清晰，接口可独立演进。 |
| 代价 | 坏处是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth*` 或对应前端 `core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```