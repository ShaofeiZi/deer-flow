---
name: smoke-test
description: DeerFlow 的端到端冒烟测试技能。用于引导完成：1) 拉取最新代码，2) 按用户偏好选择 Docker 或本地安装部署（遇到 Docker 网络问题时默认切换为本地模式），3) 验证服务可用性，4) 执行健康检查，5) 生成最终测试报告。当用户说 "run smoke test"、"smoke test deployment"、"verify installation"、"test service availability"、"end-to-end test" 或类似表达时使用。
---

# DeerFlow 冒烟测试技能

本技能用于引导 Agent 完成 DeerFlow 的完整端到端冒烟测试流程。流程覆盖代码更新、部署执行、服务可用性验证、健康检查以及最终测试报告生成，目标是在尽量短的时间内确认当前环境是否具备可运行的 DeerFlow 基础能力。

该技能同时支持 Docker 部署和本地安装部署。考虑到 Docker 镜像拉取、网络代理和容器环境差异经常会影响冒烟测试效率，默认优先使用本地安装模式；只有用户明确要求或环境更适合容器化时，才选择 Docker 模式。

## 部署模式选择

本技能支持两种部署模式：

- **本地安装模式**：推荐模式，尤其适合遇到网络问题、Docker 镜像拉取缓慢或本机已有完整开发依赖的场景。该模式会直接在本机启动 Gateway、Frontend、Nginx 等服务。
- **Docker 模式**：通过 Docker 容器运行所有服务，适合希望隔离运行环境、验证容器编排或复现容器化部署问题的场景。

**选择策略**：

- 如果用户明确要求 Docker 模式，则使用 Docker。
- 如果 Docker 镜像拉取慢、网络超时或代理配置异常，则自动切换到本地模式。
- 在没有特殊要求时，尽量默认使用本地模式，以减少网络和容器环境带来的额外变量。

## 目录结构

```text
smoke-test/
├── SKILL.md                          ← 当前文件，定义核心流程和执行逻辑
├── scripts/
│   ├── check_docker.sh               ← 检查 Docker 环境
│   ├── check_local_env.sh            ← 检查本地环境依赖
│   ├── frontend_check.sh             ← 前端页面冒烟检查
│   ├── pull_code.sh                  ← 拉取最新代码
│   ├── deploy_docker.sh              ← 执行 Docker 部署
│   ├── deploy_local.sh               ← 执行本地部署
│   └── health_check.sh               ← 执行服务健康检查
├── references/
│   ├── SOP.md                        ← 标准操作流程
│   └── troubleshooting.md            ← 常见问题排查指南
└── templates/
    ├── report.local.template.md      ← 本地模式冒烟测试报告模板
    └── report.docker.template.md     ← Docker 模式冒烟测试报告模板
```

## 标准操作流程

### 阶段 1：代码更新检查

1. **确认当前目录**：确认当前工作目录是 DeerFlow 项目根目录，避免在错误目录执行部署命令。
2. **检查 Git 状态**：查看是否存在未提交改动，防止 `git pull` 覆盖本地修改或产生冲突。
3. **拉取最新代码**：使用 `git pull origin main` 获取最新更新。
4. **确认代码更新结果**：确认最新代码已成功拉取，并记录当前 commit 信息，便于后续报告追踪。

### 阶段 2：选择部署模式并检查环境

**选择部署模式**：

- 先询问用户偏好；如果没有明确偏好，则根据网络和环境条件自动选择。
- 默认优先选择本地安装模式。

**本地模式环境检查**：

1. **检查 Node.js 版本**：要求 Node.js 22 或更高版本。
2. **检查 pnpm**：确认前端包管理器可用。
3. **检查 uv**：确认 Python 依赖管理工具可用。
4. **检查 nginx**：确认反向代理可用。
5. **检查必要端口**：确认 `2026`、`3000`、`8001` 等端口未被无关进程占用。

**Docker 模式环境检查**：

1. **检查 Docker 是否安装**：运行 `docker --version`。
2. **检查 Docker daemon 状态**：运行 `docker info`。
3. **检查 Docker Compose 是否可用**：运行 `docker compose version`。
4. **检查必要端口**：确认 `2026` 端口未被占用。

### 阶段 3：准备配置

1. **检查 `config.yaml` 是否存在**
   - 如果不存在，运行 `make config` 生成默认配置。
   - 如果已经存在，检查是否需要通过 `make config-upgrade` 合并新增配置项。
2. **检查 `.env` 文件**
   - 确认必要环境变量已经配置。
   - 重点检查模型 API Key，例如 `OPENAI_API_KEY` 或其他模型供应商密钥。

### 阶段 4：执行部署

**本地模式部署**：

1. **检查依赖**：运行 `make check`，确认本地工具链满足要求。
2. **安装依赖**：运行 `make install`，安装后端与前端依赖。
3. **可选：预拉取 sandbox 镜像**：如需容器 sandbox，可运行 `make setup-sandbox`。
4. **启动服务**：推荐运行 `make dev-daemon` 以后台模式启动；也可以运行 `make dev` 以前台模式启动。
5. **等待启动完成**：给所有服务足够的启动时间，建议等待 90 到 120 秒。

**Docker 模式部署**：

1. **初始化 Docker 环境**：运行 `make docker-init`。
2. **启动 Docker 服务**：运行 `make docker-start`。
3. **等待容器启动完成**：建议等待约 60 秒，避免服务尚未就绪时误判失败。

### 阶段 5：服务健康检查

**本地模式健康检查**：

1. **检查进程状态**：确认 Gateway、Frontend、Nginx 进程均在运行。
2. **检查前端服务**：访问 `http://localhost:2026`，确认页面可以正常加载。
3. **检查 API Gateway**：验证 `http://localhost:2026/health` 端点。
4. **检查 LangGraph 兼容 API**：验证 Gateway 暴露的 `/api/langgraph/*` 路由。
5. **执行前端路由冒烟检查**：运行 `bash .agent/skills/smoke-test/scripts/frontend_check.sh`，验证 `/workspace` 下的关键路由。

**Docker 模式健康检查**：

1. **检查容器状态**：运行 `docker ps`，确认所有容器都在运行。
2. **检查前端服务**：访问 `http://localhost:2026`，确认页面可以正常加载。
3. **检查 API Gateway**：验证 `http://localhost:2026/health` 端点。
4. **检查 LangGraph 兼容 API**：验证 Gateway 暴露的 `/api/langgraph/*` 路由。
5. **执行前端路由冒烟检查**：运行 `bash .agent/skills/smoke-test/scripts/frontend_check.sh`，验证 `/workspace` 下的关键路由。

### 可选功能验证

1. **列出可用模型**：验证模型配置能被服务正确加载。
2. **列出可用技能**：验证技能目录已正确挂载并可被读取。
3. **简单聊天测试**：发送一条简单消息，验证端到端请求链路可用。

### 阶段 6：生成测试报告

1. **收集全部测试结果**：汇总每个阶段的执行状态。
2. **记录遇到的问题**：如果有失败项，记录错误详情、复现命令和关键日志。
3. **生成最终报告**：根据选择的部署模式使用对应模板，输出完整测试报告，包括整体结论、关键测试用例明细以及前端页面/路由结果。
4. **提供后续建议**：基于测试结果给出修复、重试或环境调整建议。

## 执行规则

- **严格按顺序执行**：按上文阶段顺序推进，不要跳过前置检查。
- **保持幂等性**：每个步骤都应该尽量可重复执行，重复执行不应破坏环境。
- **错误处理**：任一步骤失败时，应停止继续执行，报告失败原因，并给出排查建议。
- **详细记录日志**：记录每个步骤的执行结果、状态和必要输出，便于最终报告复盘。
- **用户确认**：涉及覆盖配置、清理环境等潜在风险操作前，必须先让用户确认。
- **模式偏好**：优先使用本地模式，降低网络和 Docker 环境问题对冒烟测试的影响。
- **模板要求**：最终报告必须使用 `templates/` 下与部署模式匹配的模板，不要输出自由格式摘要替代模板报告。
- **报告清晰度**：执行摘要必须包含整体通过/失败结论、逐项用例说明，并明确列出前端冒烟检查结果。
- **可选阶段处理**：如果没有执行功能验证，不要在最终报告中把它单独列为“已跳过阶段”，避免制造误导性结果。

## 已知可接受告警

以下告警可能出现在冒烟测试过程中，但在对应功能未启用或不影响核心链路时，不应阻塞整体通过结论：

- Gateway 日志中的 Feishu/Lark SSL 错误，例如证书校验失败；如果未启用该渠道，可以忽略。
- Gateway 日志中关于自定义 checkpointer 缺失方法的告警，例如 `adelete_for_runs` 或 `aprune`；这些告警不影响核心功能链路。

## 关键工具

执行过程中会用到以下工具：

1. **bash**：运行 shell 命令。
2. **present_file**：展示生成的报告和重要文件。
3. **task_tool**：在步骤复杂时组织子任务。

## 成功标准

本地模式冒烟测试通过标准：

- [x] 最新代码已成功拉取。
- [x] 本地环境检查通过，包括 Node.js 22+、pnpm、uv、nginx。
- [x] 配置文件已正确准备。
- [x] `make check` 通过。
- [x] `make install` 成功完成。
- [x] `make dev` 或 `make dev-daemon` 成功启动服务。
- [x] 所有服务进程正常运行。
- [x] 前端页面可访问。
- [x] 前端路由冒烟检查通过，覆盖 `/workspace` 关键路由。
- [x] API Gateway 健康检查通过。
- [x] 测试报告完整生成。

Docker 模式冒烟测试通过标准：

- [x] 最新代码已成功拉取。
- [x] Docker 环境检查通过。
- [x] 配置文件已正确准备。
- [x] `make docker-init` 成功完成。
- [x] `make docker-start` 成功完成。
- [x] 所有 Docker 容器正常运行。
- [x] 前端页面可访问。
- [x] 前端路由冒烟检查通过，覆盖 `/workspace` 关键路由。
- [x] API Gateway 健康检查通过。
- [x] 测试报告完整生成。

## 执行前需要阅读的参考文件

开始执行前，应先阅读以下参考文件，确保操作步骤、排障策略和报告格式一致：

1. `references/SOP.md`：详细的分阶段操作说明。
2. `references/troubleshooting.md`：常见问题与解决方案。
3. `templates/report.local.template.md`：本地模式测试报告模板。
4. `templates/report.docker.template.md`：Docker 模式测试报告模板。
