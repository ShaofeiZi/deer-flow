{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 260｜ThreadMetaRow / ThreadMetaRepository 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 persistence/runtime 单文件，说明模型、仓储、provider 的调用关系。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| thread_meta/model.py | ThreadMetaRow。 |\n| thread_meta/sql.py | SQL ThreadMetaRepository。 |\n| thread_meta/memory.py | 内存实现。 |\n| thread_meta/base.py | 抽象接口。 |\n| make_thread_store | 根据 session factory 选择实现。 |\n\n```mermaid\nflowchart TD\n  ThreadsRouter --> ThreadMetaStore\n  ThreadMetaStore --> SQLRepo[ThreadMetaRepository]\n  ThreadMetaStore --> MemoryRepo[MemoryThreadMetaStore]\n  SQLRepo --> ThreadMetaRow\n  Create --> Upsert\n  Search --> MetadataFilters\n  StatusUpdate --> ThreadMetaRow\n  TitleSync --> ThreadMetaRow\n```",
      "document_id": "SWuadn7NuoRwmUxLIcImH0Loygd",
      "revision_id": 18
    }
  }
}
