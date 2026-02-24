"""Docker 沙箱模式检测逻辑的回归测试。"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "docker.sh"


def _detect_mode_with_config(config_content: str) -> str:
    """将配置内容写入临时项目根目录并执行 detect_sandbox_mode。

    Args:
        config_content: 要写入 config.yaml 的配置内容。

    Returns:
        检测到的沙箱模式字符串。
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        (tmp_root / "config.yaml").write_text(config_content)

        command = (
            f"source '{SCRIPT_PATH}' && "
            f"PROJECT_ROOT='{tmp_root}' && "
            "detect_sandbox_mode"
        )

        output = subprocess.check_output(
            ["bash", "-lc", command],
            text=True,
        ).strip()

        return output


def test_detect_mode_defaults_to_local_when_config_missing():
    """配置文件不存在时应默认为本地模式。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        command = (
            f"source '{SCRIPT_PATH}' && "
            f"PROJECT_ROOT='{tmpdir}' && "
            "detect_sandbox_mode"
        )
        output = subprocess.check_output(["bash", "-lc", command], text=True).strip()

    assert output == "local"


def test_detect_mode_local_provider():
    """本地沙箱提供者应映射为本地模式。"""
    config = """
sandbox:
  use: src.sandbox.local:LocalSandboxProvider
""".strip()

    assert _detect_mode_with_config(config) == "local"


def test_detect_mode_aio_without_provisioner_url():
    """没有 provisioner_url 的 AIO 沙箱应映射为 aio 模式。"""
    config = """
sandbox:
  use: src.community.aio_sandbox:AioSandboxProvider
""".strip()

    assert _detect_mode_with_config(config) == "aio"


def test_detect_mode_provisioner_with_url():
    """有 provisioner_url 的 AIO 沙箱应映射为 provisioner 模式。"""
    config = """
sandbox:
  use: src.community.aio_sandbox:AioSandboxProvider
  provisioner_url: http://provisioner:8002
""".strip()

    assert _detect_mode_with_config(config) == "provisioner"


def test_detect_mode_ignores_commented_provisioner_url():
    """注释掉的 provisioner_url 不应激活 provisioner 模式。"""
    config = """
sandbox:
  use: src.community.aio_sandbox:AioSandboxProvider
  # provisioner_url: http://provisioner:8002
""".strip()

    assert _detect_mode_with_config(config) == "aio"


def test_detect_mode_unknown_provider_falls_back_to_local():
    """未知的沙箱提供者应默认为本地模式。"""
    config = """
sandbox:
  use: custom.module:UnknownProvider
""".strip()

    assert _detect_mode_with_config(config) == "local"
