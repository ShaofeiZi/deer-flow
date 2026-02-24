1: ---
2: name: chart-visualization
3: 描述: 当用户希望将数据可视化时，请使用本技能。它会在 26 种可用选项中智能地选择最合适的图表类型，根据详细规格提取参数，并使用 JavaScript 脚本生成图表图片。
4: 依赖:
5:   nodejs: ">=18.0.0"
6: ---

8: # 图表可视化技能
9: 
10: 本技能提供将数据转换为可视化图表的完整工作流。它负责图表选择、参数提取和图像生成。
11: 
12: ## 工作流
 
13: 要将数据可视化，请按照以下步骤：
14: 
15: ### 1. 智能图表选择
16: 
17: 分析用户数据特征以确定最合适的图表类型。请使用以下准则（如需详细规格，请参考 `references/`）：
18: 
19: - **时间序列**：使用 `generate_line_chart`（趋势）或 `generate_area_chart`（累积趋势）。对于两个不同的刻度，使用 `generate_dual_axes_chart`。
20: - **比较**：使用 `generate_bar_chart`（分类）或 `generate_column_chart`。对于频率分布，使用 `generate_histogram_chart`。
21: - **部分对整体**：使用 `generate_pie_chart`（ Pie）或 `generate_treemap_chart`（分层）。
22: - **关系与流程**：使用 `generate_scatter_chart`（相关性）、`generate_sankey_chart`（流程）或 `generate_venn_chart`（重叠）。
23: - **地图**：使用 `generate_district_map`（区域）、`generate_pin_map`（点）或 `generate_path_map`（路线）。
24: - **层级与树状结构**：使用 `generate_organization_chart` 或 `generate_mind_map`。
25: - **专业化**：
26:     - `generate_radar_chart`：多维对比
27:     - `generate_funnel_chart`：流程阶段
28:     - `generate_liquid_chart`：百分比/进度
29:     - `generate_word_cloud_chart`：文本频率
30:     - `generate_boxplot_chart` 或 `generate_violin_chart`：统计分布
31:     - `generate_network_graph`：复杂的节点-边关系
32:     - `generate_fishbone_diagram`：因果分析
33:     - `generate_flow_diagram`：流程图
34:     - `generate_spreadsheet`：表格数据或透视表，用于结构化显示和交叉分析
35: 
36: ### 2. 参数 Extraction
37: 一旦选择了图表类型，读取 `references/` 目录中相应的文件（如 `references/generate_line_chart.md`）以识别必填和可选字段。
38: 将用户输入中的数据提取出来并映射到预期的 `args` 格式。
39: 
40: ### 3. Chart Generation
41: 调用 `scripts/generate.js` 脚本，传入 JSON 负载。
42: 
43: **Payload Format:**
44: ```json
45: {
46:   "tool": "generate_chart_type_name",
47:   "args": {
48:     "data": [...],
49:     "title": "...",
50:     "theme": "...",
51:     "style": { ... }
52:   }
53: }
54: ```
55: 
56: **Execution Command:**
57: ```bash
58: node ./scripts/generate.js '<payload_json>'
59: ```
 
60: ### 4. Result 返回
61: 脚本将输出生成的图表图像的 URL。
62: 返回给用户以下信息：
63: - 图像的 URL。
64: - 用于生成的完整 `args`（规范）。
 
65: ## 参考材料
66: 每种图表类型的详细规范位于 `references/` 目录。请查阅这些文件以确保传递给脚本的 `args` 与预期模式相符。
 
(End of file - total 68 lines)
