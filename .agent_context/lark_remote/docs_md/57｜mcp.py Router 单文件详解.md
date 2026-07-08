<title>57｜mcp.py Router 单文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲清 mcp.py 的接口职责、数据流和修改风险。
</callout>

# 1. 接口职责

| 接口 | 职责 |
|-|-|
| `GET /api/mcp/config` | 返回 masked MCP config。 |
| `PUT /api/mcp/config` | 更新 MCP config。 |
| 校验 | stdio command allowlist、shell metachar reject。 |
| 保密 | 保留旧 secret，响应 mask。 |

# 2. 运行逻辑图

```mermaid
flowchart TD
  Get[GET config] --> Load[load extensions_config]
  Load --> Mask[mask env headers oauth secrets]
  Put[PUT config] --> Admin[require admin]
  Admin --> Validate[validate stdio command allowlist]
  Validate --> Merge[merge preserving existing secrets]
  Merge --> Save[write extensions_config]
  Save --> Reset[reset mcp tools cache and session pool]
```

# 3. 修改建议

- 先改 Pydantic request/response，再改 handler。
- 涉及用户数据必须确认 owner check 或 current user。
- 前端调用方要同步更新 core API/hook。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端模块按页面、core hooks、组件拆分，是为了分离路由装配、数据状态和展示组件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是组件复用和状态管理更清晰。 |
| 代价 | 代价是一次交互会跨 React Query、localStorage、useStream 和多个组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components/workspace`。 |
| 阅读路径 | 阅读路径：先找页面入口，再找 hook 数据源，最后看组件如何消费 props/state。 |

```mermaid
flowchart TD
  A[设计动机] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[理解方式]
```