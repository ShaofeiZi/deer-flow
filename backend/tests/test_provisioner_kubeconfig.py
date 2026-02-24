"""Provisioner kubeconfig 路径处理的回归测试。"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_provisioner_module():
    """将 docker/provisioner/app.py 加载为可导入的测试模块。

    Returns:
        加载的 provisioner 模块。
    """
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "docker" / "provisioner" / "app.py"
    spec = importlib.util.spec_from_file_location("provisioner_app_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_wait_for_kubeconfig_rejects_directory(tmp_path):
    """kubeconfig 路径挂载为目录时应快速失败并给出明确错误。"""
    provisioner_module = _load_provisioner_module()
    kubeconfig_dir = tmp_path / "config_dir"
    kubeconfig_dir.mkdir()

    provisioner_module.KUBECONFIG_PATH = str(kubeconfig_dir)

    try:
        provisioner_module._wait_for_kubeconfig(timeout=1)
        raise AssertionError("目录 kubeconfig 路径应抛出 RuntimeError")
    except RuntimeError as exc:
        assert "directory" in str(exc)


def test_wait_for_kubeconfig_accepts_file(tmp_path):
    """常规文件挂载应通过就绪等待。"""
    provisioner_module = _load_provisioner_module()
    kubeconfig_file = tmp_path / "config"
    kubeconfig_file.write_text("apiVersion: v1\n")

    provisioner_module.KUBECONFIG_PATH = str(kubeconfig_file)

    # 应立即返回而不抛出异常
    provisioner_module._wait_for_kubeconfig(timeout=1)


def test_init_k8s_client_rejects_directory_path(tmp_path):
    """解析为目录的 KUBECONFIG_PATH 应被拒绝。"""
    provisioner_module = _load_provisioner_module()
    kubeconfig_dir = tmp_path / "config_dir"
    kubeconfig_dir.mkdir()

    provisioner_module.KUBECONFIG_PATH = str(kubeconfig_dir)

    try:
        provisioner_module._init_k8s_client()
        raise AssertionError("目录 kubeconfig 路径应抛出 RuntimeError")
    except RuntimeError as exc:
        assert "expected a file" in str(exc)


def test_init_k8s_client_uses_file_kubeconfig(tmp_path, monkeypatch):
    """文件存在时，provisioner 应加载 kubeconfig 文件路径。"""
    provisioner_module = _load_provisioner_module()
    kubeconfig_file = tmp_path / "config"
    kubeconfig_file.write_text("apiVersion: v1\n")

    called: dict[str, object] = {}

    def fake_load_kube_config(config_file: str):
        """模拟加载 kubeconfig 的函数。

        Args:
            config_file: kubeconfig 文件路径。
        """
        called["config_file"] = config_file

    monkeypatch.setattr(
        provisioner_module.k8s_config,
        "load_kube_config",
        fake_load_kube_config,
    )
    monkeypatch.setattr(
        provisioner_module.k8s_client,
        "CoreV1Api",
        lambda *args, **kwargs: "core-v1",
    )

    provisioner_module.KUBECONFIG_PATH = str(kubeconfig_file)

    result = provisioner_module._init_k8s_client()

    assert called["config_file"] == str(kubeconfig_file)
    assert result == "core-v1"


def test_init_k8s_client_falls_back_to_incluster_when_missing(
    tmp_path, monkeypatch
):
    """kubeconfig 文件缺失时，应尝试集群内配置。"""
    provisioner_module = _load_provisioner_module()
    missing_path = tmp_path / "missing-config"

    calls: dict[str, int] = {"incluster": 0}

    def fake_load_incluster_config():
        """模拟加载集群内配置的函数。"""
        calls["incluster"] += 1

    monkeypatch.setattr(
        provisioner_module.k8s_config,
        "load_incluster_config",
        fake_load_incluster_config,
    )
    monkeypatch.setattr(
        provisioner_module.k8s_client,
        "CoreV1Api",
        lambda *args, **kwargs: "core-v1",
    )

    provisioner_module.KUBECONFIG_PATH = str(missing_path)

    result = provisioner_module._init_k8s_client()

    assert calls["incluster"] == 1
    assert result == "core-v1"
