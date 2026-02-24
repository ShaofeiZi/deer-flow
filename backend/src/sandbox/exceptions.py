"""Sandbox 相关的异常，包含结构化的错误信息。"""


class SandboxError(Exception):
    """所有 sandbox 相关错误的基类异常。"""

    def __init__(self, message: str, details: dict | None = None):
        """
        【函数功能描述】

        初始化一个 SandboxError 异常对象，用于携带结构化的错误信息。
        该异常会保留 `message`（人类可读的错误说明）以及 `details`（可选的键值对细节），
        便于在上层统一打印、日志记录或序列化返回。

        参数:
            message: 错误主信息（用于展示给调用方/日志）。
            details: 结构化错误细节（可选），例如 sandbox_id、command、exit_code 等。

        返回:
            无。
        """

        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """
        【函数功能描述】

        将异常对象转换为字符串形式。
        若存在 `details`，会以 `key=value` 的形式拼接到主消息后，便于快速定位问题。

        参数:
            无。

        返回:
            格式化后的错误信息字符串。
        """

        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


class SandboxNotFoundError(SandboxError):
    """在找不到 sandbox 或 sandbox 不可用时抛出。"""

    def __init__(self, message: str = "Sandbox not found", sandbox_id: str | None = None):
        """
        【函数功能描述】

        构造“找不到 Sandbox”错误。
        通常用于 sandbox provider 无法根据给定的 sandbox_id 找到对应实例，
        或 sandbox 不可用/已被释放的场景。

        参数:
            message: 错误主信息。
            sandbox_id: 关联的 sandbox 标识符（可选），用于辅助排查。

        返回:
            无。
        """

        details = {"sandbox_id": sandbox_id} if sandbox_id else None
        super().__init__(message, details)
        self.sandbox_id = sandbox_id


class SandboxRuntimeError(SandboxError):
    """sandbox 运行时不可用或配置错误时抛出。"""

    pass


class SandboxCommandError(SandboxError):
    """在 sandbox 中执行命令失败时抛出。"""

    def __init__(self, message: str, command: str | None = None, exit_code: int | None = None):
        """
        【函数功能描述】

        构造“命令执行失败”错误。
        会对 command 进行截断（最多 100 个字符）以避免日志污染，同时保留 exit_code。

        参数:
            message: 错误主信息。
            command: 失败的命令（可选）。
            exit_code: 命令返回码（可选）。

        返回:
            无。
        """

        details = {}
        if command:
            details["command"] = command[:100] + "..." if len(command) > 100 else command
        if exit_code is not None:
            details["exit_code"] = exit_code
        super().__init__(message, details)
        self.command = command
        self.exit_code = exit_code


class SandboxFileError(SandboxError):
    """在 sandbox 的文件操作失败时抛出。"""

    def __init__(self, message: str, path: str | None = None, operation: str | None = None):
        """
        【函数功能描述】

        构造“文件操作失败”错误。
        适用于 read/write/list/update 等文件相关操作出现异常时，携带路径与操作类型。

        参数:
            message: 错误主信息。
            path: 相关文件/目录路径（可选）。
            operation: 发生错误的操作名称（可选），例如 "read" / "write" / "list"。

        返回:
            无。
        """

        details = {}
        if path:
            details["path"] = path
        if operation:
            details["operation"] = operation
        super().__init__(message, details)
        self.path = path
        self.operation = operation


class SandboxPermissionError(SandboxFileError):
    """在文件操作过程中发生权限错误时抛出。"""

    pass


class SandboxFileNotFoundError(SandboxFileError):
    """未找到文件或目录时抛出。"""

    pass
