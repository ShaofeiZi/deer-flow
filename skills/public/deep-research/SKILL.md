1: ---
2: name: deep-research
3: 描述: 当需要进行网络研究的任何问题时，请使用本技能。对诸如 "what is X", "explain X", "compare X and Y", "research X" 等查询，以及在内容生成任务开始前触发。提供系统性的多角度研究方法，而不是单一、肤浅的检索。遇到需要在线信息的用户问题时，请主动使用本技能。
4: ---

6: # 深度研究技能
 
8: ## 概述
 
10: 本技能提供一种系统性的方法论，用于进行彻底的网络研究。**在开始任何内容生成任务之前请加载本技能**，以确保从多角度、不同深度和多来源收集足够的信息。
 
12: ## 何时使用本技能
 
**在以下情况始终加载本技能：**
 
### 研究问题
- 用户提出 "what is X"、"explain X"、"research X"、"investigate X" 等问题
- 用户想要深入理解某个概念、技术或主题
- 问题需要来自多个来源的最新、全面信息
- 单次网络搜索不足以给出恰当的答案
 
### 内容生成（预研）
- 制作演示文稿（PPT/幻灯片）
- 设计前端界面或 UI 草图
- 撰写文章、报告或文档
- 生成视频或多媒体内容
- 任何需要真实世界信息、示例或当前数据的内容
 
## 核心原则
 
**切勿仅凭一般知识生成内容。** 你的输出质量直接依赖于事前进行的研究的质量与数量。单次搜索从来都不足够。
 
## 研究方法学
 
### 阶段 1：广泛探索
 
从广泛的检索开始，以了解全局格局：
 
1. **初步调查**：搜索主题以理解总体背景
2. **确定维度**：从初步结果中识别需要深入探讨的关键子主题、主题、角度
3. **绘制领域地图**：记录存在的不同观点、利益相关者
 
示例：
```
Topic: "AI in healthcare"
Initial searches:
- "AI healthcare applications 2024"
- "artificial intelligence medical diagnosis"
- "healthcare AI market trends"
 
Identified dimensions:
- Diagnostic AI (radiology, pathology)
- Treatment recommendation systems
- Administrative automation
- Patient monitoring
- Regulatory landscape
- Ethical considerations
```
 
### 阶段 2：深入研究
 
对每个重要维度进行有针对性的研究：
 
1. **具体查询**：针对子主题使用精确关键词
2. **多种表述**：尝试不同的关键词组合和表述
3. **获取全文**：使用 `web_fetch` 阅读重要来源的全文，而非仅是片段
4. **跟踪引用**：来源中提到的其他重要资源也要检索
 
示例：
```
Dimension: "Diagnostic AI in radiology"
Targeted searches:
- "AI radiology FDA approved systems"
- "chest X-ray AI detection accuracy"
- "radiology AI clinical trials results"
 
Then fetch and read:
- Key research papers or summaries
- Industry reports
- Real-world case studies
```
 
### 阶段 3：多样性与验证
 
通过寻求多样的信息类型来确保全面覆盖：
 
| 信息类型 | 目的 | 示例检索 |
|---------|------|---------|
- **Facts & Data** | 具体证据 | "statistics", "data", "numbers", "market size" |
- **示例 & Cases** | 真实世界应用 | "case study", "示例", "implementation" |
- **Expert Opinions** | 权威观点 | "expert analysis", "interview", "commentary" |
- **Trends & Predictions** | 未来方向 | "trends 2024", "forecast", "future of" |
- **Comparisons** | 背景与替代方案 | "vs", "comparison", "alternatives" |
- **Challenges & Criticisms** | 客观视角 | "challenges", "limitations", "criticism" |
 
### 阶段 4：综合检查
 
在进入内容生成之前，请确认：
 
- [ ] 至少从 3–5 个不同角度进行了检索
- [ ] 已获取并全文阅读了最重要的来源
- [ ] 拥有具体数据、示例与专家观点
- [ ] 既考虑到积极面，也考虑到挑战/局限
- [ ] 信息是最新且来自权威来源
 
如果任何一个否，请在生成内容前继续研究。
 
## 搜索策略提示
 
### 有效查询模式
 
```
# 以上下文为核心
❌ "AI trends"
✅ "enterprise AI adoption trends 2024"
 
# 引用权威来源提示
"[topic] research paper"
"[topic] McKinsey report"
"[topic] industry analysis"
 
 #... (后续略) 
```
 
### 何时使用 web_fetch
 
在以下情况下使用 `web_fetch` 读取全文：
 
- 检索结果高度相关且权威
- 需要超出摘要的详细信息
- 来源包含数据、案例研究或专家分析
- 来源包含发现的完整上下文
 
### 迭代细化
 
研究具有迭代性。初次检索后：
 
- 回顾所学
- 识别理解中的差距
- 构建更有针对性的查询
- 反复直到覆盖全面
 
## 质量标准
 
当你可以自信地回答以下问题时，认为研究已充分：
 
- 关键事实与数据点是什么？
- 2–3 个具体的现实世界案例是什么？
- 专家对该主题如何表达？
- 当前趋势与未来方向是什么？
- 存在的挑战或局限性是什么？
- 这个主题为何在现在相关或重要？
 
## 常见错误
 
- ❌ 研究仅停止于 1-2 次检索
- ❌ 仅依赖检索片段而未阅读全文
- ❌ 仅检索单一方面
- ❌ 忽略相悖观点或挑战
- ❌ 当前数据存在时使用过时信息
- ❌ 在研究完成前开始内容生成
 
## 输出
 
完成研究后，你应得到：
 
- 对该主题从多角度的全面理解
- 具体事实、数据点与统计数据
- 真实世界的案例与实例
- 专家观点与权威来源
- 当前趋势与相关背景
 
**只有在完成研究后，才开始内容生成**，利用收集到的信息产出高质量、信息充分的内容。
 
(End of file - total 178 lines)
