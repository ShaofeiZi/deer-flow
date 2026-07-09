<title>213｜backend/docs/FILE_UPLOAD.md 详解</title>

<callout emoji="✅">
**本章目标：**继续把 backend/docs 中重要说明拆成独立讲解文档。
</callout>

| 文档点 | 说明 |
|-|-|
| upload API | /api/threads/{id}/uploads。 |
| conversion | PDF/Office 在显式启用 `uploads.auto_convert_documents: true` 后才自动转 Markdown；默认关闭以避免在 Gateway 主机解析不受信任文件。 |
| virtual path | /mnt/user-data/uploads。 |
| UploadsMiddleware | 注入 uploaded_files 上下文。 |
| Artifacts | 上传文件也可通过 artifact URL 访问。 |

```mermaid
flowchart TD
  UI --> UploadAPI
  UploadAPI --> Validate[limits path safety]
  Validate --> Store[uploads dir]
  Store --> Convert[if auto_convert_documents enabled]
  Convert --> UploadedInfo[UploadedFileInfo]
  UploadedInfo --> UI
  Store --> UploadsMiddleware
  UploadsMiddleware --> Agent
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
sequenceDiagram
    participant FE as frontend uploads/api.ts uploadFiles
    participant R as routers/uploads.py upload_files
    participant Mgr as uploads/manager.py
    participant FC as utils/file_conversion.py
    participant SBX as sandbox_provider sandbox.update_file
    participant UM as UploadsMiddleware before_agent

    FE->>R: POST /api/threads/{id}/uploads FormData files
    R->>R: _get_upload_limits checks max_files max_file_size max_total_size
    R->>Mgr: ensure_uploads_dir thread_id
    Mgr-->>R: uploads_dir Path
    loop each UploadFile
        R->>Mgr: normalize_filename then claim_unique_filename
        R->>Mgr: _write_upload_file_with_limits streams 8192B chunks O_NOFOLLOW 0o600
        R->>Mgr: upload_virtual_path upload_artifact_url
        opt auto_convert_documents enabled and ext in CONVERTIBLE_EXTENSIONS
            R->>FC: convert_file_to_markdown file_path
            FC-->>R: md_path markdown_virtual_path
        end
    end
    R->>R: _make_file_sandbox_readable on written_paths
    opt not thread_data_mounts
        R->>SBX: _make_file_sandbox_writable then update_file virtual_path bytes
    end
    R-->>FE: UploadResponse files skipped_files

    Note over UM: later agent run reuses stored files
    UM->>Mgr: sandbox_uploads_dir scans historical files
    UM->>FC: extract_outline sibling .md per file
    UM->>UM: _files_from_kwargs reads additional_kwargs.files
    UM->>UM: _create_files_message wraps uploaded_files block
    UM-->>UM: prepends block to last HumanMessage content
```