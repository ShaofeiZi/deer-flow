{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 288｜auth repository、credential_file、reset_admin 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 auth/channel/frontend core 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| repositories/base.py | 用户 repo 抽象。 |\n| repositories/sqlite.py | SQLite user repo。 |\n| credential_file.py | 凭证文件读取。 |\n| reset_admin.py | 重置 admin 工具。 |\n| local_provider.py | 组合 repo 和认证逻辑。 |\n\n```mermaid\nflowchart TD\n  LocalProvider --> RepoBase\n  RepoBase --> SQLiteRepo\n  SQLiteRepo --> UserRow\n  CredentialFile --> LocalProvider\n  ResetAdmin --> SQLiteRepo\n  AuthRouter --> LocalProvider\n```",
      "document_id": "PDi1dfZWBoDwk1xGUb9mJ46jykf",
      "revision_id": 18
    }
  }
}
