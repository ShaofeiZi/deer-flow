<title>224｜REPLAY_E2E 文档单独详解</title>

<callout emoji="✅">
**本章目标：**继续拆剩余文档/content 模块，说明用途和关联运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| REPLAY_E2E.md | 回放 E2E 指南。 |
| record_gateway.py | 录制 gateway。 |
| run_replay_gateway.py | 回放 gateway。 |
| build_fixture_from_jsonl.py | 构建 fixture。 |
| test_replay_golden.py | golden 测试。 |

```mermaid
flowchart TD
  RealRun --> Record[record gateway]
  Record --> JSONL[jsonl trace]
  JSONL --> Fixture[build fixture]
  Fixture --> Replay[run replay gateway]
  Replay --> Golden[test replay golden]
  Golden --> Contract[contract stable]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth*` 或对应前端 `core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```