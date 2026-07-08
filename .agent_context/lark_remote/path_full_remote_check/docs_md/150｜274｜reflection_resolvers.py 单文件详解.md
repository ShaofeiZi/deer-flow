{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 274｜reflection/resolvers.py 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 tools/reflection/utils 等基础模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| resolve_class | 按 module:Class 字符串解析类。 |\n| dynamic imports | 动态导入 provider/tool 类。 |\n| 配置驱动 | ModelConfig.use 等字段依赖 resolver。 |\n| 错误处理 | 解析失败时提示配置问题。 |\n\n```mermaid\nflowchart TD\n  ConfigString[module class string] --> Parse[parse module and symbol]\n  Parse --> Import[import module]\n  Import --> GetAttr[get class or function]\n  GetAttr --> Return[return object]\n  Return --> ModelFactory\n  Return --> SandboxProvider\n  Return --> ToolFactory\n  Error --> ConfigError\n```",
      "document_id": "C21ed62UNoIzG0xQIanmuRxtydh",
      "revision_id": 18
    }
  }
}
