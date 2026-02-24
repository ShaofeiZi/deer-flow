# DeerFlow 后端

DeerFlow 是一个基于 LangGraph 的 AI 超级代理，具备沙箱执行、持久内存以及可扩展的工具集成能力。后端使 AI 代理能够执行代码、浏览网页、管理文件、将任务委派给子代理，并在对话之间保持上下文——全部在隔离的逐线程执行环境中完成。

---

## 架构

```
                        ┌──────────────────────────────────────┐
                        │          Nginx (Port 2026)           │
                        │      Unified reverse proxy           │
                        └───────┬──────────────────┬───────────┘
                                │                  │
              /api/langgraph/*  │                  │  /api/* (other)
                                ▼                  ▼
               ┌────────────────────┐  ┌────────────────────────┐
               │ LangGraph Server   │  │   Gateway API (8001)   │
               │    (Port 2024)     │  │   FastAPI REST         │
               │                    │  │                        │
               │ ┌────────────────┐ │  │ Models, MCP, Skills,   │
               │ │  Lead Agent    │ │  │ Memory, Uploads,       │
               │ │  ┌──────────┐  │ │  │ Artifacts              │
               │ │  │Middleware│  │ │  └────────────────────────┘
               │ │  │  Chain   │  │ │
               │ │  └──────────┘  │ │
               │ │  ┌──────────┐  │ │
               │ │  │  Tools   │  │ │
               │ │  └──────────┘  │ │
               │ │  ┌──────────┐  │ │
               │ │  │Subagents │  │ │
               │ │  └──────────┘  │ │
               │ └────────────────┘ │
               └────────────────────┘
```

**请求路由**（通过 Nginx）：
- `/api/langgraph/*` → LangGraph 服务器 - 代理交互、线程、流式传输
- `/api/*`（其他） → Gateway API - 模型、MCP、技能、内存、工件、上传
- `/`（非 API 请求） → Frontend - Next.js Web 界面

---

## 核心组件

### Lead Agent（主代理）

单一的 LangGraph 代理（`lead_agent`）是运行时入口，通过 `make_lead_agent(config)` 创建。它整合了：

- **带有推理与视觉支持的动态模型选择**
- **用于横向关注点处理的中间件链（9 个中间件）**
- **工具系统**，包含沙箱、MCP、社区工具和内置工具
- **用于并行任务执行的子代理委派**
- **系统提示**，含技能注入、内存上下文和工作目录指引

### 中间件链

中间件按严格顺序执行，每个中间件处理一个特定关注点：

| # | Middleware | Purpose |
|---|-----------|---------|
| 1 | **ThreadDataMiddleware** | 为每个线程创建隔离工作区/上传/输出目录 |
| 2 | **UploadsMiddleware** | 将新上传的文件注入到对话上下文 |
| 3 | **SandboxMiddleware** | 获取用于代码执行的沙箱环境 |
| 4 | **SummarizationMiddleware** | 在接近 token 限制时缩减上下文（可选） |
| 5 | **TodoListMiddleware** | 在计划模式下跟踪多步骤任务（可选） |
| 6 | **TitleMiddleware** | 在首次交换后自动生成对话标题 |
| 7 | **MemoryMiddleware** | 将对话排队以供异步内存提取 |
| 8 | **ViewImageMiddleware** | 为具备视觉能力的模型注入图像数据（有条件） |
| 9 | **ClarificationMiddleware** | 拦截澄清请求并在执行结束时中断执行（必须放在最后） |

### 沙箱系统

逐线程的隔离执行，带有虚拟路径转换：

- **抽象接口**：`execute_command`、`read_file`、`write_file`、`list_dir`
- **提供者**：`LocalSandboxProvider`（文件系统）和 `AioSandboxProvider`（Docker，在 community/）
- **虚拟路径**：`/mnt/user-data/{workspace,uploads,outputs}` → 线程特定的物理目录
- **Skills 路径**：`/mnt/skills` → `deer-flow/skills/` 目录
- **工具**：`bash`、`ls`、`read_file`、`write_file`、`str_replace`

### 子代理系统

Async task delegation with concurrent execution:

- **内置代理**：`general-purpose`（完整工具集）和 `bash`（命令专家）
- **并发性**：每轮最多 3 个子代理，15 分钟超时
- **执行**：带状态跟踪和 SSE 事件的后台线程池
- **流程**：代理调用 `task()` 工具 → 执行器在后台运行子代理 → 轮询完成情况 → 返回结果

### 内存系统

基于 LLM 的跨对话持久上下文保留：

- **自动提取**：分析对话中的用户上下文、事实与偏好
- **结构化存储**：用户上下文（工作、个人、记忆要点）、历史记录，以及基于置信度的事实
- **去抖更新**：聚合更新以最小化对 LLm 的调用（可配置等待时间）
- **系统提示注入**：将关键信息和上下文注入代理提示
- **存储**：具有基于 mtime 的缓存失效策略的 JSON 文件

### 工具生态系统

| 分类 | 工具 |
|----------|-------|
| **沙箱** | `bash`, `ls`, `read_file`, `write_file`, `str_replace` |
| **内置** | `present_files`, `ask_clarification`, `view_image`, `task` (subagent) |
| **社区** | Tavily (网络检索), Jina AI (网页抓取), Firecrawl (抓取), DuckDuckGo (图片检索) |
| **MCP** | 任何 Model Context Protocol 服务器（stdio、SSE、HTTP 传输） |
| **Skills** | 通过系统提示注入的领域特定工作流 |

### Gateway API

FastAPI 应用，提供用于前端集成的 REST 端点：

| 路由 | 目的 |
|-------|---------|
| `GET /api/models` | 列出可用的 LLM 模型 |
| `GET/PUT /api/mcp/config` | 管理 MCP 服务器配置 |
| `GET/PUT /api/skills` | 列出并管理技能 |
| `POST /api/skills/install` | 从 `.skill` 档安装技能 |
| `GET /api/memory` | 检索内存数据 |
| `POST /api/memory/reload` | 强制内存重载 |
| `GET /api/memory/config` | 内存配置 |
| `GET /api/memory/status` | 配置 + 数据的综合状态 |
| `POST /api/threads/{id}/uploads` | 上传文件（自动将 PDF/PPT/Excel/Word 转换为 Markdown） |
| `GET /api/threads/{id}/uploads/list` | 列出上传的文件 |
| `GET /api/threads/{id}/artifacts/{path}` | 提供生成的工件 |

---

## 快速开始

### 前提条件

- Python 3.12+ 
- [uv](https://docs.astral.sh/uv/) 包管理器
- 你所选 LLM 提供商的 API 密钥

### 安装

```bash
cd deer-flow

# 复制配置文件
cp config.example.yaml config.yaml

# 安装后端依赖
cd backend
make install
```

### Configuration

在项目根目录编辑 `config.yaml`：

```yaml
models:
  - name: gpt-4o
    display_name: GPT-4o
    use: langchain_openai:ChatOpenAI
    model: gpt-4o
    api_key: $OPENAI_API_KEY
    supports_thinking: false
    supports_vision: true
```

设置你的 API 密钥：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 运行

**完整应用程序**（从项目根目录）：

```bash
make dev  # Starts LangGraph + Gateway + Frontend + Nginx
```

访问地址： http://localhost:2026

**仅后端**（来自 backend 目录）：

```bash
# Terminal 1: LangGraph server
make dev

# Terminal 2: Gateway API
make gateway
```

直接访问：LangGraph 在 http://localhost:2024，Gateway 在 http://localhost:8001

---

## 项目结构

```
backend/
├── src/
│   ├── agents/                  # Agent system
│   │   ├── lead_agent/         # Main agent (factory, prompts)
│   │   ├── middlewares/        # 9 middleware components
│   │   ├── memory/             # Memory extraction & storage
│   │   └── thread_state.py    # ThreadState schema
│   ├── gateway/                # FastAPI Gateway API
│   │   ├── app.py             # Application setup
│   │   └── routers/           # 6 route modules
│   ├── sandbox/                # Sandbox execution
│   │   ├── local/             # Local filesystem provider
│   │   ├── sandbox.py         # Abstract interface
│   │   ├── tools.py           # bash, ls, read/write/str_replace
│   │   └── middleware.py      # Sandbox lifecycle
│   ├── subagents/              # Subagent delegation
│   │   ├── builtins/          # general-purpose, bash agents
│   │   ├── executor.py        # Background execution engine
│   │   └── registry.py        # Agent registry
│   ├── tools/builtins/         # Built-in tools
│   ├── mcp/                    # MCP protocol integration
│   ├── models/                 # Model factory
│   ├── skills/                 # Skill discovery & loading
│   ├── config/                 # Configuration system
│   ├── community/              # Community tools & providers
│   ├── reflection/             # Dynamic module loading
│   └── utils/                  # Utilities
├── docs/                       # Documentation
├── tests/                      # Test suite
├── langgraph.json              # LangGraph server configuration
├── pyproject.toml              # Python dependencies
├── Makefile                    # Development commands
└── Dockerfile                  # Container build
```

---

## 配置

### 主要配置（`config.yaml`）

放在项目根目录。以 `$` 开头的配置值将解析为环境变量。

关键部分：
- `models` - LLM 配置，包含类路径、API 密钥、思考/视觉标志
- `tools` - 工具定义，包含模块路径与分组
- `tool_groups` - 逻辑工具分组
- `sandbox` - 执行环境提供者
- `skills` - 技能目录路径
- `title` - 自动标题生成设置
- `summarization` - 上下文摘要设置
- `subagents` - 子代理系统（启用/禁用）
- `memory` - 内存系统设置（启用、存储、去抖、事实限制）

### Extensions 配置 (`extensions_config.json`)

MCP servers and skill states in a single file:

```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "$GITHUB_TOKEN"}
    }
  },
  "skills": {
    "pdf-processing": {"enabled": true}
  }
}
```

### 环境变量

- `DEER_FLOW_CONFIG_PATH` - 覆盖 config.yaml 的位置
- `DEER_FLOW_EXTENSIONS_CONFIG_PATH` - 覆盖 extensions_config.json 的位置
- 模型 API 密钥：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY` 等
- 工具 API 密钥：`TAVILY_API_KEY`、`GITHUB_TOKEN` 等

---

## 开发

### 命令

```bash
make install    # Install dependencies
make dev        # Run LangGraph server (port 2024)
make gateway    # Run Gateway API (port 8001)
make lint       # Run linter (ruff)
make format     # Format code (ruff)
```

### 代码风格

- **Linter/Formatter**：`ruff`
- **行长**：240 字符
- **Python**：3.12+，带类型提示
- **引号**：双引号
- **缩进**：4 个空格

### 测试

```bash
uv run pytest
```

---

## 技术栈

- **LangGraph**（1.0.6+）- 代理框架与多代理编排
- **LangChain**（1.2.3+）- LLM 抽象与工具系统
- **FastAPI**（0.115.0+）- Gateway REST API
- **langchain-mcp-adapters** - 模型上下文协议支持
- **agent-sandbox** - 沙箱化代码执行
- **markitdown** - 多格式文档转换
- **tavily-python** / **firecrawl-py** - 网络搜索与抓取

---

## 文档

- [配置指南](docs/CONFIGURATION.md)
- [体系架构详情](docs/ARCHITECTURE.md)
- [API 参考](docs/API.md)
- [文件上传](docs/FILE_UPLOAD.md)
- [路径示例](docs/PATH_EXAMPLES.md)
- [上下文摘要](docs/summarization.md)
- [Plan 模式用法](docs/plan_mode_usage.md)
- [设置指南](docs/SETUP.md)

---

## License

See the [LICENSE](../LICENSE) file in the project root.

## 贡献

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。
