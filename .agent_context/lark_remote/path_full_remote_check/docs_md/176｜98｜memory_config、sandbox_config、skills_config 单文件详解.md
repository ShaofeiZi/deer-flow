{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 98｜memory_config、sandbox_config、skills_config 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n## 本轮源码校准补充：memory_config、sandbox_config、skills_config\n\n| 文件 | 学习重点 |\n|-|-|\n| `memory_config.py` | memory 开关、存储、token counting、用户/agent 作用域。 |\n| `sandbox_config.py` | provider、路径挂载、bash/file-write、安全边界。 |\n| `skills_config.py` | public/custom skill 路径、启停、解析和 prompt 注入。 |\n\n```mermaid\nflowchart LR\n  Config[config files] --> Runtime[app config]\n  Runtime --> Memory[Memory middleware]\n  Runtime --> Sandbox[Sandbox provider]\n  Runtime --> Skills[Skill storage]\n  Skills --> Lead[lead_agent prompt/tools]\n  Memory --> Lead\n  Sandbox --> Tools[tool execution]\n```\n\n| 模块点 | 说明 |\n|-|-|\n| memory_config | memory 开关、注入、存储路径、token 计数。 |\n| sandbox_config | sandbox provider、mounts、allow_host_bash。 |\n| skills_config | skills path、container_path、候选路径。 |\n| 运行影响 | 分别影响 Dynamic/Memory middleware、SandboxProvider、SkillStorage。 |\n\n```mermaid\nflowchart TD\n  ConfigYaml --> MemoryConfig\n  ConfigYaml --> SandboxConfig\n  ConfigYaml --> SkillsConfig\n  MemoryConfig --> DynamicContext\n  MemoryConfig --> MemoryMiddleware\n  SandboxConfig --> SandboxProvider\n  SandboxConfig --> SandboxTools\n  SkillsConfig --> SkillStorage\n  SkillsConfig --> SkillActivation\n```",
      "document_id": "DR6ndS7z8oDKx1xgLqImWMN1ywg",
      "revision_id": 26
    }
  }
}
