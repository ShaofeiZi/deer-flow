{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 336｜static detection scripts 深拆\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 remaining scripts/tests/routes/package docs 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| detect_blocking_io_static.py | 静态阻塞 IO 检测。 |\n| detect_thread_boundaries.py | 线程边界检测。 |\n| detect_uv_extras.py | uv extras 检测。 |\n| check.py | 基础环境检测。 |\n\n```mermaid\nflowchart TD\n  Developer --> CheckPy\n  Developer --> BlockingStatic\n  Developer --> ThreadBoundary\n  Developer --> UVExtras\n  BlockingStatic --> Report\n  ThreadBoundary --> Report\n  UVExtras --> Report\n  CheckPy --> EnvReport\n```",
      "document_id": "AVjAdiJsRoJCHMxhjWGmn9tgy3k",
      "revision_id": 18
    }
  }
}
