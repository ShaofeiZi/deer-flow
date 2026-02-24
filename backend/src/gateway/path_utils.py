"""用于线程虚拟路径解析的共享路径解析器（如 mnt/user-data/outputs/...）。"""

import os
from pathlib import Path

from fastapi import HTTPException

from src.agents.middlewares.thread_data_middleware import THREAD_DATA_BASE_DIR

# Virtual path prefix used in sandbox environments (without leading slash for URL path matching)
VIRTUAL_PATH_PREFIX = "mnt/user-data"


def resolve_thread_virtual_path(thread_id: str, virtual_path: str) -> Path:
    """将虚拟路径解析为线程 user-data 下的实际文件系统路径。

    参数:
        thread_id: 线程 ID。
        virtual_path: 虚拟路径（示例：mnt/user-data/outputs/file.txt），
                      其中前导斜杠将被去除。

    返回:
        解析得到的实际文件系统路径 Path 对象。

    抛出:
        HTTPException: 当路径无效或超出允许访问的目录时抛出。
    """
    virtual_path = virtual_path.lstrip("/")
    if not virtual_path.startswith(VIRTUAL_PATH_PREFIX):
        raise HTTPException(status_code=400, detail=f"Path must start with /{VIRTUAL_PATH_PREFIX}")
    relative_path = virtual_path[len(VIRTUAL_PATH_PREFIX) :].lstrip("/")

    base_dir = Path(os.getcwd()) / THREAD_DATA_BASE_DIR / thread_id / "user-data"
    actual_path = base_dir / relative_path

    try:
        actual_path = actual_path.resolve()
        base_resolved = base_dir.resolve()
        if not str(actual_path).startswith(str(base_resolved)):
            raise HTTPException(status_code=403, detail="Access denied: path traversal detected")
    except (ValueError, RuntimeError):
        raise HTTPException(status_code=400, detail="Invalid path")

    return actual_path
