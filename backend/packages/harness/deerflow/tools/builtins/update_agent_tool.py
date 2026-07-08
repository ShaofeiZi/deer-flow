"""update_agent tool — let a custom agent persist updates to its own SOUL.md / config.
update_agent 工具——让自定义代理持久化更新其自身的 SOUL.md / 配置。

Bound to the lead agent only when ``runtime.context['agent_name']`` is set
(i.e. inside an existing custom agent's chat). The default agent does not see
this tool, and the bootstrap flow continues to use ``setup_agent`` for the
initial creation handshake.
仅在 ``runtime.context['agent_name']`` 设置时（即在现有自定义代理的聊天中）绑定到主代理。
默认代理看不到此工具，引导流程继续使用 ``setup_agent`` 进行初始创建握手。

The tool writes back to ``{base_dir}/users/{user_id}/agents/{agent_name}/{config.yaml,SOUL.md}``
so an agent created by one user is never visible to (or mutable by) another.
Writes are staged into temp files first; both files are renamed into place only
after both temp files are successfully written, so a partial failure cannot leave
config.yaml updated while SOUL.md still holds stale content.
工具写回到 ``{base_dir}/users/{user_id}/agents/{agent_name}/{config.yaml,SOUL.md}``，
因此一个用户创建的代理永远不会被另一个用户看到（或修改）。
写入首先暂存到临时文件；只有在两个临时文件都成功写入后，才会将两个文件重命名到位，
因此部分失败不会导致 config.yaml 已更新而 SOUL.md 仍保留旧内容。
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Annotated, Any

import yaml
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.types import Command
from pydantic import BeforeValidator

from deerflow.config.agents_config import load_agent_config, validate_agent_name
from deerflow.config.app_config import get_app_config
from deerflow.config.paths import get_paths
from deerflow.runtime.user_context import resolve_runtime_user_id
from deerflow.tools.types import Runtime

logger = logging.getLogger(__name__)

_NULLISH_STRINGS = frozenset({"null", "none", "undefined"})


def _stage_temp(path: Path, text: str) -> Path:
    """Write ``text`` into a sibling temp file and return its path.
    将 ``text`` 写入同级临时文件并返回其路径。

    The caller is responsible for ``Path.replace``-ing the temp into the target
    once every staged file is ready, or for unlinking it on failure.
    调用者负责在所有暂存文件准备好后，通过 ``Path.replace`` 将临时文件替换到目标位置，
    或在失败时取消链接。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = tempfile.NamedTemporaryFile(
        mode="w",
        dir=path.parent,
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    )
    try:
        fd.write(text)
        fd.flush()
        fd.close()
        return Path(fd.name)
    except BaseException:
        fd.close()
        Path(fd.name).unlink(missing_ok=True)
        raise


def _cleanup_temps(temps: list[Path]) -> None:
    """Best-effort removal of staged temp files.
    尽力删除暂存的临时文件。"""
    for tmp in temps:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            logger.debug("Failed to clean up temp file %s", tmp, exc_info=True)


def _is_nullish_string(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower() in _NULLISH_STRINGS


def _normalize_nullish_string(value: object) -> object:
    return None if _is_nullish_string(value) else value


OptionalText = Annotated[str | None, BeforeValidator(_normalize_nullish_string)]
OptionalStringList = Annotated[list[str] | None, BeforeValidator(_normalize_nullish_string)]


@tool(parse_docstring=True)
def update_agent(
    runtime: Runtime,
    soul: OptionalText = None,
    description: OptionalText = None,
    skills: OptionalStringList = None,
    tool_groups: OptionalStringList = None,
    model: OptionalText = None,
) -> Command:
    """Persist updates to the current custom agent's SOUL.md and config.yaml.
    持久化更新当前自定义代理的 SOUL.md 和 config.yaml。

    Use this when the user asks to refine the agent's identity, description,
    skill whitelist, tool-group whitelist, or default model. Only the fields
    you explicitly pass are updated; omitted fields keep their existing values.
    当用户要求优化代理的身份、描述、技能白名单、工具组白名单或默认模型时使用此工具。
    仅更新你显式传递的字段；省略的字段保留其现有值。

    Pass ``soul`` as the FULL replacement SOUL.md content — there is no patch
    semantics, so always start from the current SOUL and apply your edits.
    将 ``soul`` 作为完整的替换 SOUL.md 内容传递——没有补丁语义，
    因此始终从当前 SOUL 开始并应用你的编辑。

    Pass ``skills=[]`` to disable all skills for this agent. Omit ``skills``
    entirely to keep the existing whitelist. Do not pass literal strings like
    ``"null"`` / ``"none"`` / ``"undefined"`` for unchanged fields; omit those
    fields instead.
    传递 ``skills=[]`` 以禁用此代理的所有技能。完全省略 ``skills`` 以保留现有白名单。
    不要为未更改的字段传递 ``"null"`` / ``"none"`` / ``"undefined"`` 等字面字符串；
    而是省略这些字段。

    Args:
        soul: Optional full replacement SOUL.md content.
        description: Optional new one-line description.
        skills: Optional skill whitelist. ``[]`` = no skills, omit = unchanged.
        tool_groups: Optional tool-group whitelist. ``[]`` = empty, omit = unchanged.
        model: Optional model override (must match a configured model name).

    Returns:
        Command with a ToolMessage describing the result. Changes take effect
        on the next user turn (when the lead agent is rebuilt with the fresh
        SOUL.md and config.yaml).
    """
    tool_call_id = runtime.tool_call_id
    agent_name_raw: str | None = runtime.context.get("agent_name") if runtime.context else None

    def _err(message: str) -> Command:
        return Command(update={"messages": [ToolMessage(content=f"Error: {message}", tool_call_id=tool_call_id, status="error")]})

    if soul is None and description is None and skills is None and tool_groups is None and model is None:
        return _err('No fields provided. Pass at least one of: soul, description, skills, tool_groups, model. Omit unchanged fields instead of passing null-like strings such as "null", "none", or "undefined".')

    try:
        agent_name = validate_agent_name(agent_name_raw)
    except ValueError as e:
        return _err(str(e))

    if not agent_name:
        return _err("update_agent is only available inside a custom agent's chat. There is no agent_name in the current runtime context, so there is nothing to update. If you are inside the bootstrap flow, use setup_agent instead.")

    # Resolve the active user so that updates only affect this user's agent.
    # ``resolve_runtime_user_id`` prefers ``runtime.context["user_id"]`` (set by
    # the gateway from the auth-validated request) and falls back to the
    # contextvar, then DEFAULT_USER_ID. This matches setup_agent so a user
    # creating an agent and later refining it always touches the same files,
    # even if the contextvar gets lost across an async/thread boundary
    # (issue #2782 / #2862 class of bugs).
    # 解析活跃用户，使更新仅影响此用户的代理。
    # ``resolve_runtime_user_id`` 优先使用 ``runtime.context["user_id"]``（由网关
    # 从认证验证的请求中设置），然后回退到 contextvar，最后是 DEFAULT_USER_ID。
    # 这与 setup_agent 匹配，因此创建代理并随后优化它的用户始终操作相同的文件，
    # 即使 contextvar 在异步/线程边界丢失（issue #2782 / #2862 类 bug）。
    user_id = resolve_runtime_user_id(runtime)

    # Reject an unknown ``model`` *before* touching the filesystem. Otherwise
    # ``_resolve_model_name`` silently falls back to the default at runtime
    # and the user sees confusing repeated warnings on every later turn.
    # 在接触文件系统*之前*拒绝未知的 ``model``。否则 ``_resolve_model_name``
    # 会在运行时静默回退到默认值，用户会在每个后续回合看到令人困惑的重复警告。
    if model is not None and get_app_config().get_model_config(model) is None:
        return _err(f"Unknown model '{model}'. Pass a model name that exists in config.yaml's models section.")

    paths = get_paths()
    agent_dir = paths.user_agent_dir(user_id, agent_name)
    if not agent_dir.exists() and paths.agent_dir(agent_name).exists():
        return _err(f"Agent '{agent_name}' only exists in the legacy shared layout and is not scoped to a user. Run scripts/migrate_user_isolation.py to move legacy agents into the per-user layout before updating.")

    try:
        existing_cfg = load_agent_config(agent_name, user_id=user_id)
    except FileNotFoundError:
        return _err(f"Agent '{agent_name}' does not exist for the current user. Use setup_agent to create a new agent first.")
    except ValueError as e:
        return _err(f"Agent '{agent_name}' has an unreadable config: {e}")

    if existing_cfg is None:
        return _err(f"Agent '{agent_name}' could not be loaded.")

    updated_fields: list[str] = []

    # Force the on-disk ``name`` to match the directory we are writing into,
    # even if ``existing_cfg.name`` had drifted (e.g. from manual yaml edits).
    # 强制磁盘上的 ``name`` 与我们写入的目录匹配，
    # 即使 ``existing_cfg.name`` 已经偏离（例如由于手动 yaml 编辑）。
    config_data: dict[str, Any] = {"name": agent_name}
    new_description = description if description is not None else existing_cfg.description
    config_data["description"] = new_description
    if description is not None and description != existing_cfg.description:
        updated_fields.append("description")

    new_model = model if model is not None else existing_cfg.model
    if new_model is not None:
        config_data["model"] = new_model
    if model is not None and model != existing_cfg.model:
        updated_fields.append("model")

    new_tool_groups = tool_groups if tool_groups is not None else existing_cfg.tool_groups
    if new_tool_groups is not None:
        config_data["tool_groups"] = new_tool_groups
    if tool_groups is not None and tool_groups != existing_cfg.tool_groups:
        updated_fields.append("tool_groups")

    new_skills = skills if skills is not None else existing_cfg.skills
    if new_skills is not None:
        config_data["skills"] = new_skills
    if skills is not None and skills != existing_cfg.skills:
        updated_fields.append("skills")

    config_changed = bool({"description", "model", "tool_groups", "skills"} & set(updated_fields))

    # Stage every file we intend to rewrite into a temp sibling. Only after
    # *all* temp files exist do we rename them into place — so a failure on
    # SOUL.md cannot leave config.yaml already replaced.
    # 将每个我们打算重写的文件暂存到临时同级文件中。只有在*所有*临时文件都存在后，
    # 我们才将它们重命名到位——这样 SOUL.md 上的失败不会导致 config.yaml 已被替换。
    pending: list[tuple[Path, Path]] = []
    staged_temps: list[Path] = []

    try:
        agent_dir.mkdir(parents=True, exist_ok=True)

        if config_changed:
            yaml_text = yaml.dump(config_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
            config_target = agent_dir / "config.yaml"
            config_tmp = _stage_temp(config_target, yaml_text)
            staged_temps.append(config_tmp)
            pending.append((config_tmp, config_target))

        if soul is not None:
            soul_target = agent_dir / "SOUL.md"
            soul_tmp = _stage_temp(soul_target, soul)
            staged_temps.append(soul_tmp)
            pending.append((soul_tmp, soul_target))
            updated_fields.append("soul")

        # Commit phase. ``Path.replace`` is atomic per file on POSIX/NTFS and
        # the staging step above means any earlier failure has already been
        # reported. The remaining failure mode is a crash *between* two
        # ``replace`` calls, which is reported via the partial-write error
        # branch below so the caller knows which files are now on disk.
        # 提交阶段。``Path.replace`` 在 POSIX/NTFS 上对每个文件是原子操作，
        # 上述暂存步骤意味着任何更早的失败已经被报告。剩余的失败模式是在两个
        # ``replace`` 调用*之间*崩溃，这通过下面的部分写入错误分支报告，
        # 以便调用者知道哪些文件现在在磁盘上。
        committed: list[Path] = []
        try:
            for tmp, target in pending:
                tmp.replace(target)
                committed.append(target)
        except Exception as e:
            _cleanup_temps([t for t, _ in pending if t not in committed])
            if committed:
                logger.error(
                    "[update_agent] Partial write for agent '%s' (user=%s): committed=%s, failed during rename: %s",
                    agent_name,
                    user_id,
                    [p.name for p in committed],
                    e,
                    exc_info=True,
                )
                return _err(f"Partial update for agent '{agent_name}': {[p.name for p in committed]} were updated, but the rest failed ({e}). Re-run update_agent to retry the remaining fields.")
            raise

    except Exception as e:
        _cleanup_temps(staged_temps)
        logger.error("[update_agent] Failed to update agent '%s' (user=%s): %s", agent_name, user_id, e, exc_info=True)
        return _err(f"Failed to update agent '{agent_name}': {e}")

    if not updated_fields:
        return Command(update={"messages": [ToolMessage(content=f"No changes applied to agent '{agent_name}'. The provided values matched the existing config.", tool_call_id=tool_call_id)]})

    logger.info("[update_agent] Updated agent '%s' (user=%s) fields: %s", agent_name, user_id, updated_fields)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=(f"Agent '{agent_name}' updated successfully. Changed: {', '.join(updated_fields)}. The new configuration takes effect on the next user turn."),
                    tool_call_id=tool_call_id,
                )
            ]
        }
    )
