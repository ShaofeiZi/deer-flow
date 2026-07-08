{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 258｜Persistence Engine / Base / JSON Compat 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 persistence/runtime 单文件，说明模型、仓储、provider 的调用关系。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| engine.py | 初始化/关闭 SQLAlchemy engine。 |\n| base.py | DeclarativeBase。 |\n| json_compat.py | 跨 SQLite/Postgres metadata JSON 查询。 |\n| migrations/env.py | Alembic migration env。 |\n\n```mermaid\nflowchart TD\n  DatabaseConfig --> Engine[init_engine]\n  Engine --> SessionFactory\n  Base --> Models\n  JSONFilters --> JsonCompat\n  JsonCompat --> SQLWhere\n  Migrations --> Engine\n  SessionFactory --> Repositories\n```",
      "document_id": "OMmbdvG74oQZvNxJgN0mHtNuyKg",
      "revision_id": 18
    }
  }
}
