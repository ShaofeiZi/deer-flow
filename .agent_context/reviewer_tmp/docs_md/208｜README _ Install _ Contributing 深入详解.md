<title>208｜README / Install / Contributing 深入详解</title>

<callout emoji="✅">
**本章目标：**继续拆单测试族、单规格文档和根文档模块。
</callout>

| 模块点 | 说明 |
|-|-|
| README_zh.md | 中文项目介绍和快速开始。 |
| README.md | 英文项目介绍。 |
| Install.md | 给 coding agent 的安装指令。 |
| CONTRIBUTING.md | 贡献流程和开发约定。 |
| Makefile | README 中命令的实际入口。 |

```mermaid
flowchart TD
  NewUser --> README
  README --> QuickStart
  QuickStart --> Install
  Install --> Makefile
  Contributor --> Contributing
  Contributing --> DevSetup
  DevSetup --> Tests
  Tests --> PR
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
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
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