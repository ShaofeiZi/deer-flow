# 飞书文档质量补全 Spec

## Why

当前飞书文件夹内的 DeerFlow 项目讲解文档已经完成过一轮补全，但验收发现大量 Mermaid/图节点仍保留“为什么这么设计”“怎么理解”“好处/坏处”等问题式标签，不符合用户“不要是问题，要直接给答案”的核心要求。

## What Changes

- 全量清理 355 篇飞书文档中的问题式讲解标签，尤其覆盖 Mermaid/图节点、正文标题、表格字段和最终验收摘要。
- 将问题式表达统一改为答案式表达，例如“为什么这么设计”改为“设计目的”，“怎么理解”改为“阅读路径”，“好处/坏处”改为“收益/代价”。
- 对核心章节补充差异化内容，减少通用模板句，突出每个模块自己的输入、输出、关键风险、维护入口和阅读路径。
- 更新最终验收摘要，使其只声明真实完成的改动，并附上可复核的验收证据。
- 不改变项目源码；本任务只处理飞书项目讲解文档与必要的验收记录。

## Impact

- Affected specs: 飞书文档质量评估、项目讲解文档补全、文档验收证据。
- Affected code: 无源码改动；可能使用本地临时脚本/导出文件辅助批量读取、修改和验证飞书文档。

## ADDED Requirements

### Requirement: 全量答案式讲解

The system SHALL ensure the target Feishu documentation explains concepts with direct answer-style labels and content rather than question-style prompts.

#### Scenario: 清理问题式标签

- **WHEN** 验收者扫描 355 篇目标文档的正文、表格、Mermaid/图节点和摘要文档
- **THEN** 不应再发现作为讲解标签使用的“为什么这么设计”“怎么理解”“好处”“坏处”等问题式/提示式表达

#### Scenario: 使用统一替代表达

- **WHEN** 文档需要说明设计动机、阅读方式、正向价值和权衡代价
- **THEN** 应分别使用“设计目的”“阅读路径”“收益”“代价”等直接答案式标签

### Requirement: 核心章节差异化补全

The system SHALL improve the highest-value DeerFlow documentation chapters with module-specific explanation instead of generic repeated template text.

#### Scenario: 核心章节补全

- **WHEN** 用户阅读总览、Gateway、Runtime、Lead Agent、Tools/Sandbox、Frontend 主链路等核心章节
- **THEN** 文档应给出该模块特有的输入、输出、关键流程、维护入口和主要风险

### Requirement: 验收证据可信

The system SHALL keep the final validation summary consistent with actual document state.

#### Scenario: 摘要与事实一致

- **WHEN** 最终验收摘要声明某类问题已修复
- **THEN** 必须已有全量扫描或抽样验收结果支撑该声明

## MODIFIED Requirements

### Requirement: 原文档质量补全任务

飞书文件夹中的 DeerFlow 项目讲解文档不仅要覆盖完整，还必须从用户视角提供直接、可执行、可理解的答案式解释；任何补充内容不得停留在问题提示、模板化套话或未验证声明。

## REMOVED Requirements

### Requirement: 问题式引导标签

**Reason**: 用户明确要求“不要是问题，要直接给答案”，问题式标签会让文档看起来像提纲而不是讲解结果。

**Migration**: 将问题式标签迁移为答案式标签，并在标签下补充实际解释内容。
