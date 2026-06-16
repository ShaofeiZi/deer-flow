# DeerFlow 冒烟测试报告

**测试日期**：{{test_date}}  
**测试环境**：{{test_environment}}  
**部署模式**：本地模式  
**测试版本**：{{git_commit}}

---

## 执行摘要

本节用于快速判断本次本地模式冒烟测试是否通过，并展示每个关键阶段的总体结果。

| 指标 | 状态 |
|------|------|
| 测试阶段总数 | 6 |
| 通过阶段数 | {{passed_stages}} |
| 失败阶段数 | {{failed_stages}} |
| 总体结论 | **{{overall_status}}** |

### 关键测试用例

| 用例 | 结果 | 详情 |
|------|------|------|
| 代码更新检查 | {{case_code_update}} | {{case_code_update_details}} |
| 环境检查 | {{case_env_check}} | {{case_env_check_details}} |
| 配置准备 | {{case_config_prep}} | {{case_config_prep_details}} |
| 部署执行 | {{case_deploy}} | {{case_deploy_details}} |
| 健康检查 | {{case_health_check}} | {{case_health_check_details}} |
| 前端路由 | {{case_frontend_routes_overall}} | {{case_frontend_routes_details}} |

---

## 详细测试结果

### 阶段 1：代码更新检查

- [x] 确认当前目录 - {{status_dir_check}}
- [x] 检查 Git 状态 - {{status_git_status}}
- [x] 拉取最新代码 - {{status_git_pull}}
- [x] 确认代码更新结果 - {{status_git_verify}}

**阶段状态**：{{stage1_status}}

---

### 阶段 2：本地环境检查

- [x] Node.js 版本 - {{status_node_version}}
- [x] pnpm - {{status_pnpm}}
- [x] uv - {{status_uv}}
- [x] nginx - {{status_nginx}}
- [x] 端口检查 - {{status_port_check}}

**阶段状态**：{{stage2_status}}

---

### 阶段 3：配置准备

- [x] config.yaml - {{status_config_yaml}}
- [x] .env 文件 - {{status_env_file}}
- [x] 模型配置 - {{status_model_config}}

**阶段状态**：{{stage3_status}}

---

### 阶段 4：本地部署

- [x] make check - {{status_make_check}}
- [x] make install - {{status_make_install}}
- [x] make dev-daemon / make dev - {{status_local_start}}
- [x] 等待服务启动 - {{status_wait_startup}}

**阶段状态**：{{stage4_status}}

---

### 阶段 5：服务健康检查

- [x] 进程状态 - {{status_processes}}
- [x] 前端服务 - {{status_frontend}}
- [x] API Gateway - {{status_api_gateway}}
- [x] LangGraph 兼容 Gateway API - {{status_langgraph}}

**阶段状态**：{{stage5_status}}

---

### 前端路由冒烟结果

| 路由 | 状态 | 详情 |
|------|------|------|
| 首页 `/` | {{landing_status}} | {{landing_details}} |
| 工作区重定向 `/workspace` | {{workspace_redirect_status}} | 目标地址 {{workspace_redirect_target}} |
| 新建聊天 `/workspace/chats/new` | {{new_chat_status}} | {{new_chat_details}} |
| 聊天列表 `/workspace/chats` | {{chats_list_status}} | {{chats_list_details}} |
| Agent 展示页 `/workspace/agents` | {{agents_gallery_status}} | {{agents_gallery_details}} |
| 文档页 `{{docs_path}}` | {{docs_status}} | {{docs_details}} |

**汇总**：{{frontend_routes_summary}}

---

### 阶段 6：测试报告生成

- [x] 结果汇总 - {{status_summary}}
- [x] 问题记录 - {{status_issues}}
- [x] 报告生成 - {{status_report}}

**阶段状态**：{{stage6_status}}

---

## 问题记录

### 问题 1

**描述**：{{issue1_description}}  
**严重程度**：{{issue1_severity}}  
**解决方案**：{{issue1_solution}}

---

## 环境信息

### 本地依赖版本

```text
Node.js: {{node_version_output}}
pnpm: {{pnpm_version_output}}
uv: {{uv_version_output}}
nginx: {{nginx_version_output}}
```

### Git 信息

```text
Repository: {{git_repo}}
Branch: {{git_branch}}
Commit: {{git_commit}}
Commit Message: {{git_commit_message}}
```

### 配置摘要

- config.yaml 存在：{{config_exists}}
- .env 文件存在：{{env_exists}}
- 已配置模型数量：{{model_count}}

---

## 本地服务状态

| 服务 | 状态 | 端点 |
|------|------|------|
| Nginx | {{nginx_status}} | {{nginx_endpoint}} |
| Frontend | {{frontend_status}} | {{frontend_endpoint}} |
| Gateway | {{gateway_status}} | {{gateway_endpoint}} |
| Gateway LangGraph API | {{langgraph_status}} | {{langgraph_endpoint}} |

---

## 建议与下一步

### 如果测试通过

1. [ ] 访问 http://localhost:2026 开始使用 DeerFlow。
2. [ ] 如果尚未配置首选模型，请补充模型配置。
3. [ ] 查看并试用可用技能。
4. [ ] 阅读项目文档，了解更多功能和配置方式。

### 如果测试失败

1. [ ] 阅读 references/troubleshooting.md，优先排查常见问题。
2. [ ] 检查本地日志：`logs/{gateway,frontend,nginx}.log`。
3. [ ] 校验配置文件格式和关键字段。
4. [ ] 如有必要，完整重置环境：`make stop && make clean && make install && make dev-daemon`。

---

## 附录

### 完整日志

{{full_logs}}

### 测试执行人

{{tester_name}}

---

*报告生成时间：{{report_time}}*
