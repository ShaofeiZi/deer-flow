# Tasks

- [x] Task 1: 重新拉取飞书目标文件夹清单与全部 355 篇 docx 内容，建立可复核的本地检查快照
- [x] Task 2: 全量定位问题式表达残留
  - [x] SubTask 2.1: 扫描正文、标题、表格中的“为什么”“怎么理解”“好处”“坏处”等表达
  - [x] SubTask 2.2: 单独扫描 Mermaid/图节点中的问题式标签
  - [x] SubTask 2.3: 记录残留数量、文档范围和典型样例
- [x] Task 3: 批量修正问题式标签为答案式标签
  - [x] SubTask 3.1: 将“为什么这么设计”统一改为“设计目的”
  - [x] SubTask 3.2: 将“怎么理解”统一改为“阅读路径”
  - [x] SubTask 3.3: 将“好处/坏处”作为标签时统一改为“收益/代价”
  - [x] SubTask 3.4: 覆盖正文、表格、Mermaid/图节点和摘要文档
- [x] Task 4: 对核心章节做差异化补写
  - [x] SubTask 4.1: 优先处理总览、Gateway、Runtime、Lead Agent、Tools/Sandbox、Frontend 主链路
  - [x] SubTask 4.2: 为核心章节补充模块特有的输入、输出、关键流程、维护入口和风险
  - [x] SubTask 4.3: 删除或改写明显通用模板句
- [x] Task 5: 修正《354｜最终验收摘要与证据索引》
  - [x] SubTask 5.1: 摘要只保留已被验证的完成声明
  - [x] SubTask 5.2: 增加关键词扫描、核心章节抽查和渲染抽查证据
- [x] Task 6: 执行二次验收
  - [x] SubTask 6.1: 全量关键词扫描确认问题式标签不再作为讲解标签残留
  - [x] SubTask 6.2: 抽查至少 10 篇核心/边缘章节的正文、表格、Mermaid/图渲染
  - [x] SubTask 6.3: 形成最终验收结论，明确剩余风险或无风险

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 can run in parallel with Task 3 after Task 1 completes, but must避开同一文档的并发覆盖
- Task 5 depends on Task 3 and Task 4
- Task 6 depends on Task 5
