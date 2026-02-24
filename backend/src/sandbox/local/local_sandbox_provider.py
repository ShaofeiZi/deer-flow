from src.sandbox.local.local_sandbox import LocalSandbox
from src.sandbox.sandbox import Sandbox
from src.sandbox.sandbox_provider import SandboxProvider

_singleton: LocalSandbox | None = None


class LocalSandboxProvider(SandboxProvider):
    """
    【类功能描述】
    """

    def __init__(self):
        """初始化本地 sandbox 提供者及路径映射。"""
        self._path_mappings = self._setup_path_mappings()

    def _setup_path_mappings(self) -> dict[str, str]:
        """设置本地 sandbox 的路径映射。"""

        # 返回一个包含容器路径到本地路径映射的字典
        mappings = {}

        # Map skills container path to local skills directory
        try:
            from src.config import get_app_config

            config = get_app_config()
            skills_path = config.skills.get_skills_path()
            container_path = config.skills.container_path

            # Only add mapping if skills directory exists
            if skills_path.exists():
                mappings[container_path] = str(skills_path)
        except Exception as e:
            # Log but don't fail if config loading fails
            print(f"Warning: Could not setup skills path mapping: {e}")

        return mappings

    def acquire(self, thread_id: str | None = None) -> str:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        global _singleton
        if _singleton is None:
            _singleton = LocalSandbox("local", path_mappings=self._path_mappings)
        return _singleton.id

    def get(self, sandbox_id: str) -> Sandbox | None:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        if sandbox_id == "local":
            if _singleton is None:
                self.acquire()
            return _singleton
        return None

    def release(self, sandbox_id: str) -> None:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        # LocalSandbox uses singleton pattern - no cleanup needed.
        # Note: This method is intentionally not called by SandboxMiddleware
        # to allow sandbox reuse across multiple turns in a thread.
        # For Docker-based providers (e.g., AioSandboxProvider), cleanup
        # happens at application shutdown via the shutdown() method.
        pass
