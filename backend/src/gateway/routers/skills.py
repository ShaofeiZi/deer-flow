import json
import logging
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.config.extensions_config import ExtensionsConfig, SkillStateConfig, get_extensions_config, reload_extensions_config
from src.gateway.path_utils import resolve_thread_virtual_path
from src.skills import Skill, load_skills
from src.skills.loader import get_skills_root_path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["skills"])


class SkillResponse(BaseModel):
    """技能信息的响应模型。

    该模型用于表示单个技能的详细信息，包括名称、描述、许可证、分类和启用状态。

    Attributes:
        name: 技能名称。
        description: 技能功能描述。
        license: 许可证信息。
        category: 技能分类（public 或 custom）。
        enabled: 是否启用该技能。
    """

    name: str = Field(..., description="技能名称")
    description: str = Field(..., description="技能功能描述")
    license: str | None = Field(None, description="许可证信息")
    category: str = Field(..., description="技能分类（public 或 custom）")
    enabled: bool = Field(default=True, description="是否启用该技能")


class SkillsListResponse(BaseModel):
    """列出所有技能的响应模型。

    该模型用于表示技能列表的响应结构。

    Attributes:
        skills: 技能响应对象列表。
    """

    skills: list[SkillResponse]


class SkillUpdateRequest(BaseModel):
    """更新技能的请求模型。

    该模型用于接收技能启用状态的更新请求。

    Attributes:
        enabled: 是否启用该技能。
    """

    enabled: bool = Field(..., description="是否启用该技能")


class SkillInstallRequest(BaseModel):
    """从 .skill 文件安装技能的请求模型。

    该模型用于接收从线程目录安装技能的请求参数。

    Attributes:
        thread_id: .skill 文件所在的线程 ID。
        path: .skill 文件的虚拟路径（如 mnt/user-data/outputs/my-skill.skill）。
    """

    thread_id: str = Field(..., description=".skill 文件所在的线程 ID")
    path: str = Field(..., description=".skill 文件的虚拟路径（如 mnt/user-data/outputs/my-skill.skill）")


class SkillInstallResponse(BaseModel):
    """技能安装的响应模型。

    该模型用于表示技能安装操作的结果。

    Attributes:
        success: 安装是否成功。
        skill_name: 已安装的技能名称。
        message: 安装结果消息。
    """

    success: bool = Field(..., description="安装是否成功")
    skill_name: str = Field(..., description="已安装的技能名称")
    message: str = Field(..., description="安装结果消息")


ALLOWED_FRONTMATTER_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}


def _validate_skill_frontmatter(skill_dir: Path) -> tuple[bool, str, str | None]:
    """验证技能目录的 SKILL.md frontmatter。

    检查 SKILL.md 文件是否存在、格式是否正确、必需字段是否完整，
    以及字段值是否符合命名规范。

    Args:
        skill_dir: 技能目录路径。

    Returns:
        元组，包含三个元素：
        - 是否验证通过
        - 验证消息
        - 技能名称（验证通过时）
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "未找到 SKILL.md 文件", None

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "未找到 YAML frontmatter", None

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "frontmatter 格式无效", None

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "frontmatter 必须是 YAML 字典格式", None
    except yaml.YAMLError as e:
        return False, f"frontmatter 中的 YAML 无效：{e}", None

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_PROPERTIES
    if unexpected_keys:
        return False, f"SKILL.md frontmatter 中存在意外的键：{', '.join(sorted(unexpected_keys))}", None

    if "name" not in frontmatter:
        return False, "frontmatter 中缺少 'name' 字段", None
    if "description" not in frontmatter:
        return False, "frontmatter 中缺少 'description' 字段", None

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"name 必须是字符串类型，实际为 {type(name).__name__}", None
    name = name.strip()
    if not name:
        return False, "name 不能为空", None

    if not re.match(r"^[a-z0-9-]+$", name):
        return False, f"name '{name}' 应为短横线命名格式（仅限小写字母、数字和短横线）", None
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"name '{name}' 不能以短横线开头或结尾，也不能包含连续短横线", None
    if len(name) > 64:
        return False, f"name 过长（{len(name)} 个字符）。最大长度为 64 个字符。", None

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"description 必须是字符串类型，实际为 {type(description).__name__}", None
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "description 不能包含尖括号（< 或 >）", None
        if len(description) > 1024:
            return False, f"description 过长（{len(description)} 个字符）。最大长度为 1024 个字符。", None

    return True, "技能验证通过！", name


def _skill_to_response(skill: Skill) -> SkillResponse:
    """将 Skill 对象转换为 SkillResponse。

    Args:
        skill: Skill 对象实例。

    Returns:
        转换后的 SkillResponse 对象。
    """
    return SkillResponse(
        name=skill.name,
        description=skill.description,
        license=skill.license,
        category=skill.category,
        enabled=skill.enabled,
    )


@router.get(
    "/skills",
    response_model=SkillsListResponse,
    summary="列出所有技能",
    description="检索公共和自定义目录中所有可用技能的列表。",
)
async def list_skills() -> SkillsListResponse:
    """列出所有可用技能。

    从公共和自定义目录加载所有技能（包括已禁用的技能），
    并返回技能列表响应。

    Returns:
        SkillsListResponse: 包含所有技能列表的响应对象。

    Raises:
        HTTPException: 加载技能失败时抛出 500 错误。
    """
    try:
        skills = load_skills(enabled_only=False)
        return SkillsListResponse(skills=[_skill_to_response(skill) for skill in skills])
    except Exception as e:
        logger.error(f"加载技能失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"加载技能失败：{str(e)}")


@router.get(
    "/skills/{skill_name}",
    response_model=SkillResponse,
    summary="获取技能详情",
    description="按名称检索特定技能的详细信息。",
)
async def get_skill(skill_name: str) -> SkillResponse:
    """按名称获取特定技能。

    根据技能名称查找并返回该技能的详细信息。

    Args:
        skill_name: 要获取的技能名称。

    Returns:
        SkillResponse: 技能详细信息响应对象。

    Raises:
        HTTPException: 技能不存在时抛出 404 错误，获取失败时抛出 500 错误。
    """
    try:
        skills = load_skills(enabled_only=False)
        skill = next((s for s in skills if s.name == skill_name), None)

        if skill is None:
            raise HTTPException(status_code=404, detail=f"未找到技能 '{skill_name}'")

        return _skill_to_response(skill)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取技能 {skill_name} 失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取技能失败：{str(e)}")


@router.put(
    "/skills/{skill_name}",
    response_model=SkillResponse,
    summary="更新技能",
    description="通过修改 skills_state_config.json 文件更新技能的启用状态。",
)
async def update_skill(skill_name: str, request: SkillUpdateRequest) -> SkillResponse:
    """更新技能的启用状态。

    将技能的启用状态更新到配置文件，并重新加载配置缓存。

    Args:
        skill_name: 要更新的技能名称。
        request: 包含启用状态的更新请求。

    Returns:
        SkillResponse: 更新后的技能信息响应对象。

    Raises:
        HTTPException: 技能不存在时抛出 404 错误，更新失败时抛出 500 错误。
    """
    try:
        skills = load_skills(enabled_only=False)
        skill = next((s for s in skills if s.name == skill_name), None)

        if skill is None:
            raise HTTPException(status_code=404, detail=f"未找到技能 '{skill_name}'")

        config_path = ExtensionsConfig.resolve_config_path()
        if config_path is None:
            config_path = Path.cwd().parent / "extensions_config.json"
            logger.info(f"未找到现有的扩展配置文件。将在以下位置创建新配置：{config_path}")

        extensions_config = get_extensions_config()

        extensions_config.skills[skill_name] = SkillStateConfig(enabled=request.enabled)

        config_data = {
            "mcpServers": {name: server.model_dump() for name, server in extensions_config.mcp_servers.items()},
            "skills": {name: {"enabled": skill_config.enabled} for name, skill_config in extensions_config.skills.items()},
        }

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        logger.info(f"技能配置已更新并保存至：{config_path}")

        reload_extensions_config()

        skills = load_skills(enabled_only=False)
        updated_skill = next((s for s in skills if s.name == skill_name), None)

        if updated_skill is None:
            raise HTTPException(status_code=500, detail=f"更新后无法重新加载技能 '{skill_name}'")

        logger.info(f"技能 '{skill_name}' 的启用状态已更新为 {request.enabled}")
        return _skill_to_response(updated_skill)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新技能 {skill_name} 失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新技能失败：{str(e)}")


@router.post(
    "/skills/install",
    response_model=SkillInstallResponse,
    summary="安装技能",
    description="从线程的 user-data 目录安装一个 .skill 文件中的技能（ZIP 压缩包）。",
)
async def install_skill(request: SkillInstallRequest) -> SkillInstallResponse:
    """从 .skill 文件安装技能。

    该 .skill 文件是一个 ZIP 归档，包含一个技能目录（含 SKILL.md）以及可选资源（脚本、引用、资源等）。

    Args:
        request: 包含 thread_id 和 .skill 文件的虚拟路径的安装请求。

    Returns:
        SkillInstallResponse: 具有技能名称和状态消息的安装结果。

    Raises:
        HTTPException:
            - 400: 路径无效或文件不是有效的 .skill 文件
            - 403: 访问被拒绝（检测到路径遍历）
            - 404: 文件未找到
            - 409: 技能已存在
            - 500: 安装失败
    """
    try:
        skill_file_path = resolve_thread_virtual_path(request.thread_id, request.path)

        if not skill_file_path.exists():
            raise HTTPException(status_code=404, detail=f"未找到技能文件：{request.path}")

        if not skill_file_path.is_file():
            raise HTTPException(status_code=400, detail=f"路径不是文件：{request.path}")

        if not skill_file_path.suffix == ".skill":
            raise HTTPException(status_code=400, detail="文件必须具有 .skill 扩展名")

        if not zipfile.is_zipfile(skill_file_path):
            raise HTTPException(status_code=400, detail="文件不是有效的 ZIP 归档")

        skills_root = get_skills_root_path()
        custom_skills_dir = skills_root / "custom"

        custom_skills_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with zipfile.ZipFile(skill_file_path, "r") as zip_ref:
                zip_ref.extractall(temp_path)

            extracted_items = list(temp_path.iterdir())
            if len(extracted_items) == 0:
                raise HTTPException(status_code=400, detail="技能归档为空")

            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                skill_dir = extracted_items[0]
            else:
                skill_dir = temp_path

            is_valid, message, skill_name = _validate_skill_frontmatter(skill_dir)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"无效的技能：{message}")

            if not skill_name:
                raise HTTPException(status_code=400, detail="无法确定技能名称")

            target_dir = custom_skills_dir / skill_name
            if target_dir.exists():
                raise HTTPException(status_code=409, detail=f"技能 '{skill_name}' 已存在。请先删除或使用不同的名称。")

            shutil.copytree(skill_dir, target_dir)

        logger.info(f"技能 '{skill_name}' 已成功安装至 {target_dir}")
        return SkillInstallResponse(success=True, skill_name=skill_name, message=f"技能 '{skill_name}' 安装成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"安装技能失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"安装技能失败：{str(e)}")
