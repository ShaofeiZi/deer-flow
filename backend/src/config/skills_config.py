from pathlib import Path

from pydantic import BaseModel, Field


class SkillsConfig(BaseModel):
    """技能系统配置。

    该类用于配置技能系统的路径和容器挂载路径。

    Attributes:
        path: 技能目录的路径。如果未指定，默认为 backend 目录的 ../skills。
        container_path: 技能在沙箱容器中挂载的路径。
    """

    path: str | None = Field(
        default=None,
        description="技能目录的路径。如果未指定，默认为 backend 目录的 ../skills",
    )
    container_path: str = Field(
        default="/mnt/skills",
        description="技能在沙箱容器中挂载的路径",
    )

    def get_skills_path(self) -> Path:
        """获取解析后的技能目录路径。

        Returns:
            技能目录的路径。
        """
        if self.path:
            path = Path(self.path)
            if not path.is_absolute():
                path = Path.cwd() / path
            return path.resolve()
        else:
            from src.skills.loader import get_skills_root_path

            return get_skills_root_path()

    def get_skill_container_path(self, skill_name: str, category: str = "public") -> str:
        """获取特定技能的完整容器路径。

        Args:
            skill_name: 技能名称（目录名称）。
            category: 技能类别（public 或 custom）。

        Returns:
            技能在容器中的完整路径。
        """
        return f"{self.container_path}/{category}/{skill_name}"
