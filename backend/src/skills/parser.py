import re
from pathlib import Path

from .types import Skill


def parse_skill_file(skill_file: Path, category: str) -> Skill | None:
    """解析 SKILL.md 文件并提取元数据。

    Args:
        skill_file: SKILL.md 文件的路径
        category: 技能的类别（'public' 或 'custom'）

    Returns:
        如果解析成功则返回 Skill 对象，否则返回 None
    """
    if not skill_file.exists() or skill_file.name != "SKILL.md":
        return None

    try:
        content = skill_file.read_text(encoding="utf-8")

        # 提取 YAML front matter
        # 模式：---\nkey: value\n---
        front_matter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)

        if not front_matter_match:
            return None

        front_matter = front_matter_match.group(1)

        # 解析 YAML front matter（简单的键值对解析）
        metadata = {}
        for line in front_matter.split("\n"):
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        # 提取必需字段
        name = metadata.get("name")
        description = metadata.get("description")

        if not name or not description:
            return None

        license_text = metadata.get("license")

        return Skill(
            name=name,
            description=description,
            license=license_text,
            skill_dir=skill_file.parent,
            skill_file=skill_file,
            category=category,
            enabled=True,  # 默认启用，实际状态来自配置文件
        )

    except Exception as e:
        print(f"解析技能文件 {skill_file} 时出错：{e}")
        return None
