"""Single source of truth for the config hot-reload boundary.

Bytedance/deer-flow issue #3144: gateway request dependencies resolve
``AppConfig`` through ``get_app_config()`` on every request, so per-run
fields take effect on the next message without restarting the gateway.
The fields listed in this module are the **infrastructure** subset that
the gateway captures once at startup — engines, singletons, IM clients,
the logging handler — and that therefore require a process restart to
change at runtime.

The registry covers two kinds of entries:

- Top-level ``AppConfig`` fields (``database``, ``checkpointer``,
  ``run_events``, ``stream_bridge``, ``sandbox``, ``log_level``). For
  these, :func:`format_field_description` produces the standardised
  ``"startup-only: ..."`` prefix that the matching Pydantic
  ``Field(description=...)`` carries, so the boundary surfaces in IDE
  hover next to the field itself.
- Top-level ``config.yaml`` sections that are not part of the
  ``AppConfig`` schema (``channels``). These cannot be standardised at
  the schema level, so the registry is their only canonical location.

Any future "needs restart" scanner — operator tooling, lint hooks, doc
generators — should drive off this registry rather than re-parsing
prose.

配置热重载边界的唯一真相来源。

Bytedance/deer-flow issue #3144：网关请求依赖在每次请求时通过 ``get_app_config()`` 解析 ``AppConfig``，
因此每次运行的字段在下一条消息时生效，无需重启网关。本模块中列出的字段是网关在启动时捕获一次的**基础设施**子集 —
引擎、单例、IM 客户端、日志处理器 — 因此需要在运行时重启进程才能更改。

注册表涵盖两种条目：

- 顶层 ``AppConfig`` 字段（``database``、``checkpointer``、``run_events``、``stream_bridge``、``sandbox``、``log_level``）。
  对于这些字段，:func:`format_field_description` 生成标准化的 ``"startup-only: ..."`` 前缀，
  匹配的 Pydantic ``Field(description=...)`` 携带该前缀，因此边界在 IDE 悬停时显示在字段旁边。
- 不属于 ``AppConfig`` schema 的顶层 ``config.yaml`` 节（``channels``）。这些无法在 schema 级别标准化，
  因此注册表是它们唯一的规范位置。

任何未来的"需要重启"扫描器 — 运维工具、lint 钩子、文档生成器 — 都应基于此注册表而非重新解析文本。
"""

from __future__ import annotations

from collections.abc import Iterator

#: The standardised prefix every restart-required field description starts
#: with. ``test_reload_boundary`` enforces both directions: registered
#: fields must use this prefix in the schema, and any schema field using
#: this prefix must be in the registry.
#: 每个需要重启的字段描述都以这个标准化前缀开头。``test_reload_boundary`` 双向强制执行：
#: 已注册的字段必须在 schema 中使用此前缀，且任何使用此前缀的 schema 字段必须在注册表中。
STARTUP_ONLY_PREFIX = "startup-only:"


#: Restart-required field paths mapped to the human-readable reason.
#:
#: The reason text is what surfaces in ``Field(description=...)``, so it
#: must explain *what* code captures the snapshot — not just that the
#: field is restart-required — so an operator changing the value knows
#: which subsystem to restart.
#: 需要重启的字段路径映射到人类可读的原因。
#:
#: 原因文本会显示在 ``Field(description=...)`` 中，因此必须解释*什么*代码捕获了快照 —
#: 而不仅仅是该字段需要重启 — 以便更改值的运维人员知道需要重启哪个子系统。
STARTUP_ONLY_FIELDS: dict[str, str] = {
    "database": ("init_engine_from_config() runs once during langgraph_runtime() startup; the SQLAlchemy engine holds the connection pool and is not rebuilt on config.yaml edits."),
    "checkpointer": ("make_checkpointer() binds the persistent checkpointer once at startup, including SQLite WAL / busy_timeout settings."),
    "run_events": ("make_run_event_store() picks the memory- vs SQL-backed implementation at startup and is frozen onto app.state.run_events_config to stay paired with the underlying event store."),
    "stream_bridge": ("make_stream_bridge() constructs the stream-bridge singleton once during startup."),
    "sandbox": ("get_sandbox_provider() caches the provider singleton (``_default_sandbox_provider``); a different ``sandbox.use`` class path only takes effect on next process start."),
    "log_level": (
        "apply_logging_level() runs only during app.py startup; it sets the deerflow/app logger levels and may lower root handler thresholds so configured messages can propagate. A freshly reloaded AppConfig does not retrigger it."
    ),
    # Not part of the AppConfig Pydantic schema — channel credentials are
    # consumed directly by ``start_channel_service()`` once at lifespan
    # startup and the live channel clients are not rebuilt on
    # config.yaml edits.
    # 不属于 AppConfig Pydantic schema — 频道凭据在生命周期启动时由 ``start_channel_service()`` 直接消费一次，
    # 活跃的频道客户端不会在 config.yaml 编辑时重建。
    "channels": ("start_channel_service() is invoked once during startup; the live IM channel clients (Feishu, Slack, Telegram, DingTalk) are not rebuilt when channels.* changes."),
}


def iter_startup_only_field_paths() -> Iterator[str]:
    """Yield every registered restart-required field path.

    生成每个已注册的需要重启的字段路径。
    """
    return iter(STARTUP_ONLY_FIELDS)


def is_startup_only_field(field_path: str) -> bool:
    """Return ``True`` when *field_path* is registered as restart-required.

    Accepts only top-level paths (``"database"``, ``"sandbox"`` etc.);
    nested keys like ``"database.url"`` are not modelled here because the
    boundary is per-section, not per-leaf.

    当 *field_path* 被注册为需要重启时返回 ``True``。

    仅接受顶层路径（``"database"``、``"sandbox"`` 等）；嵌套键如 ``"database.url"`` 不在此建模，
    因为边界是按节而不是按叶子的。
    """
    return field_path in STARTUP_ONLY_FIELDS


def format_field_description(field_path: str, *, field_doc: str | None = None) -> str:
    """Build the standardised description for a registered field.

    Used inside ``AppConfig`` ``Field(description=...)`` so the hover
    text in IDEs matches the registry and the drift tests can pin one
    side against the other.

    Args:
        field_path: A registered top-level field path (e.g. ``"log_level"``).
        field_doc: Optional human-facing description for the field itself
            (allowed values, semantics, etc.). When supplied, it is
            appended after the ``startup-only:`` marker block separated by
            a blank line so IDE hover shows both the restart-required
            reason *and* the field's normal documentation. Composition
            keeps the marker as the leading token machine-readable tooling
            pivots on while restoring the prose that ``Field(description=)``
            used to carry before the registry took over.

    Raises:
        KeyError: when *field_path* is not registered. This is deliberate
            — silently returning a placeholder would let a typo bypass
            the drift coverage.

    为已注册字段构建标准化描述。

    在 ``AppConfig`` ``Field(description=...)`` 中使用，使 IDE 中的悬停文本与注册表匹配，
    并且漂移测试可以将一侧与另一侧进行对比。

    Args:
        field_path: 已注册的顶层字段路径（例如 ``"log_level"``）。
        field_doc: 字段本身的可选面向用户的描述（允许的值、语义等）。当提供时，它会附加在
            ``startup-only:`` 标记块之后，用空行分隔，使 IDE 悬停同时显示需要重启的原因
            *和* 字段的正常文档。组合方式保留了标记作为机器可读工具所依赖的前导标记，
            同时恢复了 ``Field(description=)`` 在注册表接管之前所携带的文本。

    Raises:
        KeyError: 当 *field_path* 未注册时。这是有意为之 — 静默返回占位符会让拼写错误绕过漂移覆盖。
    """
    reason = STARTUP_ONLY_FIELDS[field_path]
    header = f"{STARTUP_ONLY_PREFIX} {reason}"
    if field_doc is None:
        return header
    return f"{header}\n\n{field_doc.strip()}"
