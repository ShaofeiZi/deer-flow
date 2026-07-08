{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 277｜uploads/manager.py 单文件详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 tools/reflection/utils 等基础模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| normalize_filename | 文件名归一化。 |\n| claim_unique_filename | 同批次重名处理。 |\n| open_upload_file_no_symlink | 防 symlink 写入。 |\n| delete_file_safe | 安全删除。 |\n| upload_virtual_path/artifact_url | 生成虚拟路径和 artifact URL。 |\n\n```mermaid\nflowchart TD\n  UploadRequest --> Normalize[normalize filename]\n  Normalize --> Claim[claim unique filename]\n  Claim --> Open[open no symlink]\n  Open --> Write[write chunks]\n  Write --> VirtualPath[virtual path]\n  VirtualPath --> ArtifactURL\n  Delete --> SafeDelete[delete file safe]\n  List --> Enrich[enrich file listing]\n```",
      "document_id": "HyYtdAH4xomM54x4SFomKpCoyHg",
      "revision_id": 18
    }
  }
}
