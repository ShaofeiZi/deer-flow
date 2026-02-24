from pathlib import Path

from .parser import parse_skill_file
from .types import Skill


def get_skills_root_path() -> Path:
    """获取技能目录的根路径。

    Returns:
        技能目录的路径（deer-flow/skills）
    """
    # backend 目录是当前文件的父目录的父目录的父目录
    backend_dir = Path(__file__).resolve().parent.parent.parent
    # skills 目录是 backend 目录的兄弟目录
    skills_dir = backend_dir.parent / "skills"
    return skills_dir


def load_skills(skills_path: Path | None = None, use_config: bool = True, enabled_only: bool = False) -> list[Skill]:
    """从技能目录加载所有技能。

    扫描公共和自定义技能目录，解析 SKILL.md 文件以提取元数据。
    启用状态由 skills_state_config.json 文件决定。

    Args:
        skills_path: 可选的自定义技能目录路径。
                     如果未提供且 use_config 为 True，则使用配置中的路径。
                     否则默认为 deer-flow/skills
        use_config: 是否从配置加载技能路径（默认：True）
        enabled_only: 如果为 True，只返回已启用的技能（默认：False）

    Returns:
        按名称排序的 Skill 对象列表
    """
    if skills_path is None:
        if use_config:
            try:
                from src.config import get_app_config

                config = get_app_config()
                skills_path = config.skills.get_skills_path()
            except Exception:
                # 如果配置失败则回退到默认值
                skills_path = get_skills_root_path()
        else:
            skills_path = get_skills_root_path()

    if not skills_path.exists():
        return []

    skills = []

    # 扫描 public 和 custom 目录
    for category in ["public", "custom"]:
        category_path = skills_path / category
        if not category_path.exists() or not category_path.is_dir():
            continue

        # 每个子目录都是一个潜在的技能
        for skill_dir in category_path.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            skill = parse_skill_file(skill_file, category=category)
            if skill:
                skills.append(skill)

    # 加载技能状态配置并更新启用状态
    # 注意：我们使用 ExtensionsConfig.from_file() 而不是 get_extensions_config()
    # 以始终从磁盘读取最新配置。这确保通过 Gateway API（在独立进程中运行）
    # 所做的更改在加载技能时立即反映到 LangGraph Server 中。
    try:
        from src.config.extensions_config import ExtensionsConfig

        extensions_config = ExtensionsConfig.from_file()
        for skill in skills:
            skill.enabled = extensions_config.is_skill_enabled(skill.name, skill.category)
    except Exception as e:
        # 如果配置加载失败，默认全部启用
        print(f"警告：加载扩展配置失败：{e}")

    # 如果请求，按启用状态过滤
    if enabled_only:
        skills = [skill for skill in skills if skill.enabled]

    # 按名称排序以保持一致顺序
    skills.sort(key=lambda s: s.name)

    return skills
