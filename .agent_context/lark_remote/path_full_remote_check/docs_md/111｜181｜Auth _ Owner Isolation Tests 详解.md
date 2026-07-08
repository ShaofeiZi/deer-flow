{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>181｜Auth / Owner Isolation Tests 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| test_auth\\*.py | 认证配置、错误、middleware、类型系统。 |\n| test_owner_isolation.py | owner 隔离。 |\n| test_stateless_runs_owner_isolation.py | stateless runs owner 隔离。 |\n| \\_router_auth_helpers.py | router auth 测试辅助。 |\n\n```mermaid\nflowchart TD\n  AuthCode --> AuthTests\n  OwnerCode --> OwnerTests\n  AuthTests --> TestClient\n  OwnerTests --> TestClient\n  TestClient --> Request[authenticated requests]\n  Request --> Assertions[401 403 owner checks]\n  Assertions --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这组测试验证认证身份如何进入 Gateway 请求，并在 threads/runs/uploads/artifacts/memory/feedback 等资源访问时保持 owner isolation。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 401/403/404、CSRF、admin 初始化、无 auth 兼容和跨用户隔离都有明确回归点。 |\n| 代价 | 一次鉴权问题可能跨 middleware、permission decorator、repository owner filter、ContextVar 和测试 helper。 |\n| 重点代码 | `backend/app/gateway/auth_middleware.py`、`backend/app/gateway/authz.py`、`backend/app/gateway/auth/`、`backend/tests/_router_auth_helpers.py`、`backend/tests/test_owner_isolation.py`、`backend/tests/test_stateless_runs_owner_isolation.py`。 |\n| 阅读路径 | 先看请求如何得到 current user，再看 owner_check 如何查资源归属，最后用测试确认未授权、跨用户和 auth-disabled 分支。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "GBSFdiLNWoCqsRxIcBgmvnmQyWe",
      "revision_id": 18
    }
  }
}
