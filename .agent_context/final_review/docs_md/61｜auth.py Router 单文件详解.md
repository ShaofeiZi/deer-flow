<title>61｜auth.py Router 单文件详解</title>

<callout emoji="✅">
**本章目标：**单独讲清本地登录、注册、初始化、OAuth callback 和安全限制。
</callout>

# 1. 模块职责

| 对象 | 说明 |
|-|-|
| `login_local` | 表单登录，校验密码，设置 HttpOnly session cookie。 |
| `register` | 注册普通用户。 |
| `initialize_admin` | 首次启动初始化 admin。 |
| `change_password` | 修改密码并刷新会话。 |
| `oauth_login/callback` | OAuth provider 登录入口。 |

# 2. 运行逻辑图

```mermaid
sequenceDiagram
  participant UI as Login UI
  participant Auth as auth.py
  participant Provider as AuthProvider
  participant Cookie as Cookies
  UI->>Auth: login/register/initialize
  Auth->>Auth: rate limit and password validation
  Auth->>Provider: create or verify user
  Provider-->>Auth: user
  Auth->>Cookie: session and csrf cookie
  Cookie-->>UI: authenticated
```

# 3. 排障与修改建议

- 先确认调用方和数据源，再改 schema。
- 涉及用户数据必须确认鉴权和 owner check。
- 涉及缓存需要同步 invalidate 或 reset。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |
| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |
| 重点代码 | 标题对应的源码、测试或文档入口。 |
| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |

```mermaid
stateDiagram-v2
  [*] --> NoRecord
  NoRecord --> Tracked: login_local fail
  Tracked --> Tracked: fail again count under 5
  Tracked --> Locked: 5th fail lock 300s
  Tracked --> NoRecord: login_local success
  Locked --> Locked: request 429 within lock
  Locked --> NoRecord: lock_until passed evict
```
