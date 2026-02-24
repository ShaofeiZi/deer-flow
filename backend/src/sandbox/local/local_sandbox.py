import os
import subprocess
from pathlib import Path

from src.sandbox.local.list_dir import list_dir
from src.sandbox.sandbox import Sandbox


class LocalSandbox(Sandbox):
    """
    【类功能描述】
    """

    def __init__(self, id: str, path_mappings: dict[str, str] | None = None):
        """初始化本地 sandbox，支持可选的路径映射。"""

        # 参数：
        #   id: Sandbox 标识符
        #   path_mappings: 将容器路径映射到本地路径的字典，例如：{"/mnt/skills": "/absolute/path/to/skills"}
        super().__init__(id)
        self.path_mappings = path_mappings or {}

    def _resolve_path(self, path: str) -> str:
        """使用映射将容器路径解析为实际的本地路径。"""

        # 参数：
        #   path: 可能是容器路径的路径字符串
        # 返回：解析后的本地路径
        path_str = str(path)

        # Try each mapping (longest prefix first for more specific matches)
        for container_path, local_path in sorted(self.path_mappings.items(), key=lambda x: len(x[0]), reverse=True):
            if path_str.startswith(container_path):
                # Replace the container path prefix with local path
                relative = path_str[len(container_path) :].lstrip("/")
                resolved = str(Path(local_path) / relative) if relative else local_path
                return resolved

        # No mapping found, return original path
        return path_str

    def _reverse_resolve_path(self, path: str) -> str:
        """将本地路径反向映射回容器路径（使用映射）。"""

        # 参数：
        #   path: 本地路径
        # 返回：若存在映射则得到容器路径，否则返回原始路径
        path_str = str(Path(path).resolve())

        # Try each mapping (longest local path first for more specific matches)
        for container_path, local_path in sorted(self.path_mappings.items(), key=lambda x: len(x[1]), reverse=True):
            local_path_resolved = str(Path(local_path).resolve())
            if path_str.startswith(local_path_resolved):
                # Replace the local path prefix with container path
                relative = path_str[len(local_path_resolved) :].lstrip("/")
                resolved = f"{container_path}/{relative}" if relative else container_path
                return resolved

        # No mapping found, return original path
        return path_str

    def _reverse_resolve_paths_in_output(self, output: str) -> str:
        """在输出中将本地路径反向解析为容器路径。"""

        # 参数：
        #   output: 可能包含本地路径的输出字符串
        # 返回：将本地路径解析为容器路径后的输出
        import re

        # Sort mappings by local path length (longest first) for correct prefix matching
        sorted_mappings = sorted(self.path_mappings.items(), key=lambda x: len(x[1]), reverse=True)

        if not sorted_mappings:
            return output

        # Create pattern that matches absolute paths
        # Match paths like /Users/... or other absolute paths
        result = output
        for container_path, local_path in sorted_mappings:
            local_path_resolved = str(Path(local_path).resolve())
            # Escape the local path for use in regex
            escaped_local = re.escape(local_path_resolved)
            # Match the local path followed by optional path components
            pattern = re.compile(escaped_local + r"(?:/[^\s\"';&|<>()]*)?")

            def replace_match(match: re.Match) -> str:
                """
                【函数功能描述】
                
                参数:
                    【参数名】: 【参数描述】
                
                返回:
                    【返回值描述】
                """

                matched_path = match.group(0)
                return self._reverse_resolve_path(matched_path)

            result = pattern.sub(replace_match, result)

        return result

    def _resolve_paths_in_command(self, command: str) -> str:
        """在命令字符串中将容器路径解析为本地路径。"""

        # 参数：
        #   command: 可能包含容器路径的命令字符串
        # 返回：将容器路径解析为本地路径后的命令
        import re

        # Sort mappings by length (longest first) for correct prefix matching
        sorted_mappings = sorted(self.path_mappings.items(), key=lambda x: len(x[0]), reverse=True)

        # Build regex pattern to match all container paths
        # Match container path followed by optional path components
        if not sorted_mappings:
            return command

        # Create pattern that matches any of the container paths
        patterns = [re.escape(container_path) + r"(?:/[^\s\"';&|<>()]*)??" for container_path, _ in sorted_mappings]
        pattern = re.compile("|".join(f"({p})" for p in patterns))

        def replace_match(match: re.Match) -> str:
            """
            【函数功能描述】
            
            参数:
                【参数名】: 【参数描述】
            
            返回:
                【返回值描述】
            """

            matched_path = match.group(0)
            return self._resolve_path(matched_path)

        return pattern.sub(replace_match, command)

    def execute_command(self, command: str) -> str:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        # Resolve container paths in command before execution
        resolved_command = self._resolve_paths_in_command(command)

        result = subprocess.run(
            resolved_command,
            executable="/bin/zsh",
            shell=True,
            capture_output=True,
            text=True,
            timeout=600,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nStd Error:\n{result.stderr}" if output else result.stderr
        if result.returncode != 0:
            output += f"\nExit Code: {result.returncode}"

        final_output = output if output else "(no output)"
        # Reverse resolve local paths back to container paths in output
        return self._reverse_resolve_paths_in_output(final_output)

    def list_dir(self, path: str, max_depth=2) -> list[str]:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        resolved_path = self._resolve_path(path)
        entries = list_dir(resolved_path, max_depth)
        # Reverse resolve local paths back to container paths in output
        return [self._reverse_resolve_paths_in_output(entry) for entry in entries]

    def read_file(self, path: str) -> str:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        resolved_path = self._resolve_path(path)
        with open(resolved_path) as f:
            return f.read()

    def write_file(self, path: str, content: str, append: bool = False) -> None:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        resolved_path = self._resolve_path(path)
        dir_path = os.path.dirname(resolved_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        mode = "a" if append else "w"
        with open(resolved_path, mode) as f:
            f.write(content)

    def update_file(self, path: str, content: bytes) -> None:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        resolved_path = self._resolve_path(path)
        dir_path = os.path.dirname(resolved_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(resolved_path, "wb") as f:
            f.write(content)
