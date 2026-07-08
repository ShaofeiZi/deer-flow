{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>224｜REPLAY_E2E 文档单独详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆剩余文档/content 模块，说明用途和关联运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| REPLAY_E2E.md | 回放 E2E 指南。 |\n| record_gateway.py | 录制 gateway。 |\n| run_replay_gateway.py | 回放 gateway。 |\n| build_fixture_from_jsonl.py | 构建 fixture。 |\n| test_replay_golden.py | golden 测试。 |\n\n```mermaid\nflowchart TD\n  RealRun --> Record[record gateway]\n  Record --> JSONL[jsonl trace]\n  JSONL --> Fixture[build fixture]\n  Fixture --> Replay[run replay gateway]\n  Replay --> Golden[test replay golden]\n  Golden --> Contract[contract stable]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**Replay E2E 用 key-free fixture 固定跨栈协议与渲染合同，避免真实模型、网络和密钥波动影响回归。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | backend SSE golden 与 full-stack render 分层验证，能分别捕获协议漂移和前端渲染漂移。 |\n| 代价 | fixture 与真实录制需要维护；hash miss、multi-run order、无 checkpoint 场景必须显式失败而不是静默通过。 |\n| 重点代码 | `backend/docs/REPLAY_E2E.md`、`backend/tests/replay_provider.py`、`backend/scripts/run_replay_gateway.py`、`backend/tests/test_replay_golden.py`、`frontend/tests/e2e-real-backend/`。 |\n| 阅读路径 | 先读 REPLAY_E2E.md 的两层验证模型，再看 record/build fixture，最后跑 backend golden 与 real-backend Playwright。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "CivLd9lDQoJJmDxSkoamHa4Iyng",
      "revision_id": 18
    }
  }
}
