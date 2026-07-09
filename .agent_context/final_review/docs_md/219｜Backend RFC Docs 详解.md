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
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
sequenceDiagram
  participant Client
  participant MW as AuthMiddleware
  participant JWT as auth/jwt decode_token
  participant Prov as LocalAuthProvider get_user
  participant RP as require_permission
  participant TMS as ThreadMetaStore check_access
  participant H as delete_thread_data
  Client->>MW: DELETE /api/threads by id, access_token cookie
  MW->>JWT: decode_token cookie
  JWT-->>MW: TokenPayload or TokenError
  MW->>Prov: get_user payload.sub
  Prov-->>MW: User or 401 user_not_found
  MW->>MW: stamp request.state.user and user_context
  MW->>RP: threads delete owner_check require_existing
  RP->>TMS: check_access thread_id user.id
  TMS-->>RP: allow or deny 404
  RP->>H: invoke delete_thread_data
  H-->>Client: ThreadDeleteResponse
```