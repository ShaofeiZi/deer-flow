from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    """表示一个技能，包含其元数据和文件路径。"""

    name: str
    description: str
    license: str | None
    skill_dir: Path
    skill_file: Path
    category: str  # 'public' 或 'custom'
    enabled: bool = False  # 该技能是否启用

    @property
    def skill_path(self) -> str:
        """返回从技能根目录到此技能目录的相对路径。"""
        return self.skill_dir.name

    def get_container_path(self, container_base_path: str = "/mnt/skills") -> str:
        """获取此技能在容器中的完整路径。

        Args:
            container_base_path: 技能在容器中挂载的基础路径

        Returns:
            技能目录的完整容器路径
        """
        return f"{container_base_path}/{self.category}/{self.skill_dir.name}"

    def get_container_file_path(self, container_base_path: str = "/mnt/skills") -> str:
        """获取此技能主文件（SKILL.md）在容器中的完整路径。

        Args:
            container_base_path: 技能在容器中挂载的基础路径

        Returns:
            技能 SKILL.md 文件的完整容器路径
        """
        return f"{container_base_path}/{self.category}/{self.skill_dir.name}/SKILL.md"

    def __repr__(self) -> str:
        """返回技能的字符串表示。"""
        return f"Skill(name={self.name!r}, description={self.description!r}, category={self.category!r})"
