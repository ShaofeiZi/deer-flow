---
name: find-skills
描述: 帮助用户发现和安装代理技能，当他们询问"如何做 X"、"查找 X 的技能"、"是否有技能可以..."，或表达扩展能力的兴趣时使用。当用户寻找可能作为可安装技能存在的功能时，应使用此技能。
---

# 查找技能

本技能帮助您从开放代理技能生态系统发现和安装技能。

## 何时使用此技能

当用户：

- 询问"如何做 X"，其中 X 可能是具有现有技能的常见任务
- 说"查找 X 的技能"或"是否有 X 的技能"
- 询问"你能做 X"，其中 X 是专业能力
- 表达扩展代理能力的兴趣
- 想要搜索工具、模板或工作流
- 提到他们希望在某特定领域（设计、测试、部署等）获得帮助

## 什么是技能 CLI？

技能 CLI（`npx skills`）是开放代理技能生态系统的包管理器。技能是模块化包，通过专业知识、工作流和工具扩展代理能力。

**关键命令：**

- `npx skills find [query]` - 交互式或按关键词搜索技能
- `npx skills check` - 检查技能更新
- `npx skills update` - 更新所有已安装技能

**浏览技能：** https://skills.sh/

## 如何帮助用户查找技能

### 第一步：理解他们需要什么

当用户询问某方面的帮助时，识别：

1. 领域（例如 React、测试、设计、部署）
2. 具体任务（例如编写测试、创建动画、审查 PR）
3. 这是否是足够常见的任务，可能存在技能

### 第二步：搜索技能

使用相关查询运行查找命令：

```bash
npx skills find [query]
```

例如：

- 用户问"如何让我的 React 应用更快？" → `npx skills find react performance`
- 用户问"你能帮我审查 PR 吗？" → `npx skills find pr review`
- 用户问"我需要创建变更日志" → `npx skills find changelog`

命令将返回如下结果：

```
Install with bash /path/to/skill/scripts/install-skill.sh vercel-labs/agent-skills@vercel-react-best-practices

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 第三步：向用户展示选项

当找到相关技能时，向用户展示：

1. 技能名称及其功能
2. 他们可以运行的安装命令
3. 在 skills.sh 了解更多的链接

示例响应：

```
我找到了一个可能有帮助的技能！"vercel-react-best-practices" 技能提供来自 Vercel 工程团队的 React 和 Next.js 性能优化指南。

要安装它：
bash /path/to/skill/scripts/install-skill.sh vercel-labs/agent-skills@vercel-react-best-practices

了解更多：https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 第四步：安装技能

如果用户想继续，使用 `install-skill.sh` 脚本安装技能并自动链接到项目：

```bash
bash /path/to/skill/scripts/install-skill.sh <owner/repo@skill-name>
```

例如，如果用户想安装 `vercel-react-best-practices`：

```bash
bash /path/to/skill/scripts/install-skill.sh vercel-labs/agent-skills@vercel-react-best-practices
```

脚本将安装技能到全局 `skills/custom/`

## 常见技能类别

搜索时，考虑这些常见类别：

| 类别        | 示例查询                          |
| --------------- | ---------------------------------------- |
| Web 开发 | react, nextjs, typescript, css, tailwind |
| 测试         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| 文档   | docs, readme, changelog, api-docs        |
| 代码质量    | review, lint, refactor, best-practices   |
| 设计          | ui, ux, design-system, accessibility     |
| 生产力    | workflow, automation, git                |

## 有效搜索的技巧

1. **使用特定关键词**："react testing" 比仅 "testing" 更好
2. **尝试替代术语**：如果 "deploy" 不起作用，尝试 "deployment" 或 "ci-cd"
3. **查看热门来源**：许多技能来自 `vercel-labs/agent-skills` 或 `ComposioHQ/awesome-claude-skills`

## 当没有找到技能时

如果没有相关技能存在：

1. 承认没有找到现有技能
2. 提议使用通用能力直接帮助完成任务
3. 建议用户可以使用 `npx skills init` 创建自己的技能

示例：

```
我搜索了与"xyz"相关的技能但没有找到匹配项。
我仍然可以直接帮助您完成此任务！您想让我继续吗？

如果这是您经常做的事情，您可以创建自己的技能：
npx skills init my-xyz-skill
```
