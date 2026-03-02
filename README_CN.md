# 🦌 DeerFlow - 2.0

DeerFlow（**D**eep **E**xploration and **E**fficient **R**esearch **Flow**，深度探索与高效研究流程）是一个开源的**超级代理框架**，通过编排**子代理**、**记忆**和**沙箱**来完成几乎任何任务——由**可扩展技能**驱动。

https://github.com/user-attachments/assets/a8bcadc4-e040-4cf2-8fda-dd768b999c18

> [!注意]
> **DeerFlow 2.0 是完全重写的版本。** 它与 v1 没有共享代码。如果您正在寻找原始的深度研究框架，它在 [`1.x` 分支](https://github.com/bytedance/deer-flow/tree/main-1.x) 上维护——那里的贡献仍然欢迎。活跃开发已转移到 2.0。

## 官方网站

在我们的官方网站了解更多并查看**真实演示**。

**[deerflow.tech](https://deerflow.tech/)**

---

## 目录

- [快速开始](#快速开始)
- [沙箱模式](#沙箱模式)
- [从深度研究到超级代理框架](#从深度研究到超级代理框架)
- [核心特性](#核心特性)
  - [技能与工具](#技能与工具)
  - [子代理](#子代理)
  - [沙箱与文件系统](#沙箱与文件系统)
  - [上下文工程](#上下文工程)
  - [长期记忆](#长期记忆)
- [推荐模型](#推荐模型)
- [文档](#文档)
- [贡献](#贡献)
- [许可证](#许可证)
- [致谢](#致谢)
- [Star 历史](#star-历史)

## 快速开始

### 配置

1. **克隆 DeerFlow 仓库**

   ```bash
   git clone https://github.com/bytedance/deer-flow.git
   cd deer-flow
   ```

2. **生成本地配置文件**

   在项目根目录（`deer-flow/`）运行：

   ```bash
   make config
   ```

   此命令根据提供的示例模板创建本地配置文件。

3. **配置您首选的模型**

   编辑 `config.yaml` 并定义至少一个模型：

   ```yaml
   models:
     - name: gpt-4                       # 内部标识符
       display_name: GPT-4               # 显示名称
       use: langchain_openai:ChatOpenAI  # LangChain 类路径
       model: gpt-4                      # API 模型标识符
       api_key: $OPENAI_API_KEY          # API 密钥（推荐使用环境变量）
       max_tokens: 4096                  # 每次请求的最大 token 数
       temperature: 0.7                  # 采样温度
   ```

4. **为配置的模型设置 API 密钥**

   选择以下方法之一：

- 方式 A：编辑项目根目录的 `.env` 文件（推荐）

   ```bash
   TAVILY_API_KEY=your-tavily-api-key
   OPENAI_API_KEY=your-openai-api-key
   # 根据需要添加其他提供商密钥
   ```

- 方式 B：在 shell 中导出环境变量

   ```bash
   export OPENAI_API_KEY=your-openai-api-key
   ```

- 方式 C：直接编辑 `config.yaml`（生产环境不推荐）

   ```yaml
   models:
     - name: gpt-4
       api_key: your-actual-api-key-here  # 替换占位符
   ```

### 运行应用

#### 方式 1：Docker（推荐）

以一致的环境快速开始的最快方式：

1. **初始化并启动**：
   ```bash
   make docker-init    # 拉取沙箱镜像（仅首次或镜像更新时）
   make docker-start   # 启动服务（自动从 config.yaml 检测沙箱模式）
   ```

   `make docker-start` 现在仅在 `config.yaml` 使用 provisioner 模式（`sandbox.use: src.community.aio_sandbox:AioSandboxProvider` 配合 `provisioner_url`）时启动 `provisioner`。

2. **访问**：http://localhost:2026

详细 Docker 开发指南请参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

#### 方式 2：本地开发

如果您更喜欢在本地运行服务：

1. **检查前置条件**：
   ```bash
   make check  # 验证 Node.js 22+、pnpm、uv、nginx
   ```

2. **（可选）预先拉取沙箱镜像**：
   ```bash
   # 如果使用 Docker/容器沙箱，推荐执行
   make setup-sandbox
   ```

3. **启动服务**：
   ```bash
   make dev
   ```

4. **访问**：http://localhost:2026

### 高级
#### 沙箱模式

DeerFlow 支持多种沙箱执行模式：
- **本地执行**（直接在主机上运行沙箱代码）
- **Docker 执行**（在隔离的 Docker 容器中运行沙箱代码）
- **Kubernetes Docker 执行**（通过 provisioner 服务在 Kubernetes Pod 中运行沙箱代码）

对于 Docker 开发，服务启动遵循 `config.yaml` 沙箱模式。在本地/Docker 模式下，不会启动 `provisioner`。

请参阅 [沙箱配置指南](backend/docs/CONFIGURATION.md#sandbox) 配置您首选的模式。

#### MCP 服务器

DeerFlow 支持可配置的 MCP 服务器和技能来扩展其能力。
详细说明请参见 [MCP 服务器指南](backend/docs/MCP_SERVER.md)。

## 从深度研究到超级代理框架

DeerFlow 最初是一个深度研究框架——社区将其发扬光大。自发布以来，开发者将其推向了研究之外：构建数据管道、生成幻灯片、创建仪表板、自动化内容工作流。这些都是我们从未预料到的用途。

这告诉我们一些重要的东西：DeerFlow 不仅仅是一个研究工具。它是一个**框架**——一个为代理提供实际完成工作所需基础设施的运行时。

所以我们从头重建了它。

DeerFlow 2.0 不再是您需要组装的框架。它是一个超级代理框架——开箱即用，完全可扩展。基于 LangGraph 和 LangChain 构建，它自带代理所需的一切：文件系统、记忆、技能、沙箱执行，以及为复杂多步骤任务规划和生成子代理的能力。

直接使用。或者拆解它，让它成为您的。

## 核心特性

### 技能与工具

技能是让 DeerFlow 能做**几乎任何事**的关键。

一个标准的代理技能是一个结构化的能力模块——一个定义工作流、最佳实践和支持资源引用的 Markdown 文件。DeerFlow 内置了研究、报告生成、幻灯片创建、网页、图像和视频生成等技能。但真正的力量在于可扩展性：添加您自己的技能、替换内置技能，或将它们组合成复合工作流。

技能是渐进式加载的——仅在任务需要时加载，而非一次性全部加载。这保持了上下文窗口的精简，使 DeerFlow 即使在使用对 token 敏感的模型时也能良好工作。

工具遵循相同的理念。DeerFlow 自带核心工具集——网络搜索、网页获取、文件操作、bash 执行——并通过 MCP 服务器和 Python 函数支持自定义工具。可以替换任何东西。可以添加任何东西。

```
# 沙箱容器内的路径
/mnt/skills/public
├── research/SKILL.md
├── report-generation/SKILL.md
├── slide-creation/SKILL.md
├── web-page/SKILL.md
└── image-generation/SKILL.md

/mnt/skills/custom
└── your-custom-skill/SKILL.md      ← 您的
```

### 子代理

复杂任务很少能一次性完成。DeerFlow 会分解它们。

主导代理可以即时生成子代理——每个子代理都有自己的作用域上下文、工具和终止条件。子代理在可能的情况下并行运行，报告结构化结果，主导代理将所有内容综合成连贯的输出。

这就是 DeerFlow 处理耗时数分钟到数小时任务的方式：一个研究任务可能会分散成十几个子代理，每个探索不同的角度，然后汇聚成一份报告——或一个网站——或一套带有生成视觉效果的幻灯片。一个框架，多双手。

### 沙箱与文件系统

DeerFlow 不仅仅是*谈论*做事。它有自己的计算机。

每个任务在隔离的 Docker 容器中运行，拥有完整的文件系统——技能、工作区、上传、输出。代理读取、写入和编辑文件。它执行 bash 命令和代码。它查看图像。全部沙箱化、全部可审计、会话间零污染。

这就是拥有工具访问权限的聊天机器人和拥有实际执行环境的代理之间的区别。

```
# 沙箱容器内的路径
/mnt/user-data/
├── uploads/          ← 您的文件
├── workspace/        ← 代理的工作目录
└── outputs/          ← 最终交付物
```

### 上下文工程

**隔离的子代理上下文**：每个子代理在自己的隔离上下文中运行。这意味着子代理无法看到主代理或其他子代理的上下文。这很重要，确保子代理能够专注于手头的任务，而不被主代理或其他子代理的上下文分散注意力。

**摘要**：在会话内，DeerFlow 积极管理上下文——摘要已完成的子任务、将中间结果卸载到文件系统、压缩不再立即相关的内容。这使其能够在长多步骤任务中保持敏锐，而不会爆掉上下文窗口。

### 长期记忆

大多数代理在对话结束的那一刻就会忘记一切。DeerFlow 会记住。

跨会话，DeerFlow 构建关于您的个人资料、偏好和积累知识的持久记忆。您使用得越多，它就越了解您——您的写作风格、您的技术栈、您的重复工作流。记忆存储在本地，由您控制。

## 推荐模型

DeerFlow 与模型无关——它适用于任何实现 OpenAI 兼容 API 的 LLM。话虽如此，它在支持以下特性的模型上表现最佳：

- **长上下文窗口**（100k+ tokens）用于深度研究和多步骤任务
- **推理能力**用于自适应规划和复杂分解
- **多模态输入**用于图像理解和视频理解
- **强大的工具使用**用于可靠的函数调用和结构化输出

## 文档

- [贡献指南](CONTRIBUTING.md) - 开发环境设置和工作流
- [配置指南](backend/docs/CONFIGURATION.md) - 设置和配置说明
- [架构概览](backend/CLAUDE.md) - 技术架构详情
- [后端架构](backend/README.md) - 后端架构和 API 参考

## 贡献

我们欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解开发设置、工作流和指南。

回归测试覆盖包括 `backend/tests/` 中的 Docker 沙箱模式检测和 provisioner kubeconfig-path 处理测试。

## 许可证

本项目是开源的，采用 [MIT 许可证](./LICENSE)。

## 致谢

DeerFlow 建立在开源社区令人难以置信的工作之上。我们深深感谢所有项目和贡献者的努力，是他们使 DeerFlow 成为可能。真的，我们站在巨人的肩膀上。

我们要向以下项目致以诚挚的感谢，感谢他们的宝贵贡献：

- **[LangChain](https://github.com/langchain-ai/langchain)**：他们出色的框架为我们的 LLM 交互和链提供动力，实现了无缝集成和功能。
- **[LangGraph](https://github.com/langchain-ai/langgraph)**：他们创新的多代理编排方法对于实现 DeerFlow 复杂的工作流至关重要。

这些项目体现了开源协作的变革力量，我们很自豪能在它们的基础上构建。

### 核心贡献者

衷心感谢 `DeerFlow` 的核心作者，他们的愿景、热情和奉献使这个项目得以实现：

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

您坚定的承诺和专业知识一直是 DeerFlow 成功的推动力。我们很荣幸有您引领这段旅程。

## Star 历史

[![Star History Chart](https://api.star-history.org/svg?repos=bytedance/deer-flow&type=Date)](https://star-history.com/#bytedance/deer-flow&Date)
