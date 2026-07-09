<title>319｜Skill Creator Scripts 单文件族详解</title>

<callout emoji="✅">
**本章目标：**继续拆更细 backend/frontend/skill scripts 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| init_skill.py | 初始化 skill。 |
| run_eval.py | 运行评估。 |
| generate_report.py | 生成报告。 |
| improve_description.py | 优化描述。 |
| package_skill.py | 打包 skill。 |
| agents/\* | 分析/比较/评分子代理。 |

```mermaid
flowchart TD
  CreateSkill --> InitSkill
  InitSkill --> Eval[run eval]
  Eval --> Report[generate report]
  Report --> Improve[improve description]
  Improve --> Package[package skill]
  Agents --> Eval
  Package --> SkillArchive
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该文档说明前端 UI primitive、workspace 组件或页面模块的职责、状态来源和渲染分支。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 组件边界清晰后，UI 问题可按 props/state/hook/route 快速定位。 |
| 代价 | 一次交互常跨页面、hook、context 和展示组件，需要按数据流追踪。 |
| 重点代码 | 标题对应的 `frontend/src/app/`、`frontend/src/components/` 或 `frontend/src/core/` 文件。 |
| 阅读路径 | 先看组件输入输出，再看状态来源，最后看事件回调如何改变 UI。 |

```mermaid
flowchart TD
  Start["run_loop main"] --> Split["split_eval_set stratified holdout"]
  Split --> Iter["iteration 1 to max_iterations"]
  Iter --> Eval["run_eval train+test batch"]
  Eval --> Workers["ProcessPoolExecutor run_single_query"]
  Workers --> Claude["claude -p stream-json"]
  Claude --> Detect["detect Skill Read tool_use"]
  Detect --> Rate["trigger_rate vs threshold"]
  Rate --> Check{"train all pass?"}
  Check -->|"yes"| Best["pick best by test score"]
  Check -->|"no"| Improve["improve_description claude -p blinded history"]
  Improve --> Limit{"over 1024 chars?"}
  Limit -->|"yes"| Shorten["rewrite shorten call"]
  Limit -->|"no"| Next["set current_description"]
  Shorten --> Next
  Next --> Iter
  Best --> Report["generate_html final"]
```