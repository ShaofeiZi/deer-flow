from abc import ABC, abstractmethod


class Sandbox(ABC):
    """沙箱环境的抽象基类"""

    _id: str

    def __init__(self, id: str):
        self._id = id

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def execute_command(self, command: str) -> str:
        """在 sandbox 中执行 bash 命令。

        参数:
            command: 要执行的命令。

        返回:
            命令的标准输出或错误输出。
        """
        pass

    @abstractmethod
    def read_file(self, path: str) -> str:
        """读取文件的内容。

        参数:
            path: 要读取的文件的绝对路径。

        返回:
            文件的内容。
        """
        pass

    @abstractmethod
    def list_dir(self, path: str, max_depth=2) -> list[str]:
        """列出目录的内容。

        参数:
            path: 要列出的目录的绝对路径。
            max_depth: 要遍历的最大深度。默认值为 2。

        返回:
            目录的内容。
        """
        pass

    @abstractmethod
    def write_file(self, path: str, content: str, append: bool = False) -> None:
        """将内容写入文件。

        参数:
            path: 要写入的文件的绝对路径。
            content: 要写入文件的文本内容。
            append: 是否将内容追加到文件中。若 False，文件将被创建或覆盖。
        """
        pass

    @abstractmethod
    def update_file(self, path: str, content: bytes) -> None:
        """使用二进制内容更新文件。

        参数:
            path: 要更新的文件的绝对路径。
            content: 要写入文件的二进制内容。
        """
        pass
