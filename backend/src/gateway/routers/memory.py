"""全局内存数据的 API 路由，用于检索和管理对话记忆数据。"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.agents.memory.updater import get_memory_data, reload_memory_data
from src.config.memory_config import get_memory_config

router = APIRouter(prefix="/api", tags=["memory"])


class ContextSection(BaseModel):
    """上下文段落模型（用于用户上下文与历史上下文）。

    该模型用于表示上下文段落的内容和更新时间。

    Attributes:
        summary: 摘要内容。
        updatedAt: 最后更新时间戳。
    """

    summary: str = Field(default="", description="摘要内容")
    updatedAt: str = Field(default="", description="最后更新时间戳")


class UserContext(BaseModel):
    """用户上下文模型，包含工作区、个人信息与当前重点。

    该模型用于组织用户相关的上下文信息，包括工作上下文、
    个人上下文和当前关注事项。

    Attributes:
        workContext: 工作上下文段落。
        personalContext: 个人上下文段落。
        topOfMind: 当前关注事项段落。
    """

    workContext: ContextSection = Field(default_factory=ContextSection)
    personalContext: ContextSection = Field(default_factory=ContextSection)
    topOfMind: ContextSection = Field(default_factory=ContextSection)


class HistoryContext(BaseModel):
    """历史上下文模型，包含最近活动、早期上下文与长期背景信息。

    该模型用于组织历史相关的上下文信息，包括最近几个月的活动、
    早期上下文和长期背景信息。

    Attributes:
        recentMonths: 最近几个月的上下文段落。
        earlierContext: 早期上下文段落。
        longTermBackground: 长期背景信息段落。
    """

    recentMonths: ContextSection = Field(default_factory=ContextSection)
    earlierContext: ContextSection = Field(default_factory=ContextSection)
    longTermBackground: ContextSection = Field(default_factory=ContextSection)


class Fact(BaseModel):
    """记忆事实模型，用于表示可用于对话记忆的事实条目。

    该模型用于存储从对话中提取的事实信息，包括内容、分类、
    置信度、创建时间和来源等属性。

    Attributes:
        id: 事实的唯一标识符。
        content: 事实内容。
        category: 事实分类。
        confidence: 置信度分数（0-1）。
        createdAt: 创建时间戳。
        source: 来源线程 ID。
    """

    id: str = Field(..., description="事实的唯一标识符")
    content: str = Field(..., description="事实内容")
    category: str = Field(default="context", description="事实分类")
    confidence: float = Field(default=0.5, description="置信度分数（0-1）")
    createdAt: str = Field(default="", description="创建时间戳")
    source: str = Field(default="unknown", description="来源线程 ID")


class MemoryResponse(BaseModel):
    """内存数据的响应模型，包含版本、时间戳、用户与历史上下文以及事实列表。

    该模型用于表示完整的内存数据响应结构。

    Attributes:
        version: 内存数据模式版本。
        lastUpdated: 最后更新时间戳。
        user: 用户上下文信息。
        history: 历史上下文信息。
        facts: 事实列表。
    """

    version: str = Field(default="1.0", description="内存数据模式版本")
    lastUpdated: str = Field(default="", description="最后更新时间戳")
    user: UserContext = Field(default_factory=UserContext)
    history: HistoryContext = Field(default_factory=HistoryContext)
    facts: list[Fact] = Field(default_factory=list)


class MemoryConfigResponse(BaseModel):
    """内存系统配置的响应模型，描述启用状态与存储参数。

    该模型用于表示内存系统的配置信息。

    Attributes:
        enabled: 是否启用内存功能。
        storage_path: 内存存储文件路径。
        debounce_seconds: 内存更新的防抖时间（秒）。
        max_facts: 最大存储事实数量。
        fact_confidence_threshold: 事实的最低置信度阈值。
        injection_enabled: 是否启用内存注入。
        max_injection_tokens: 内存注入的最大令牌数。
    """

    enabled: bool = Field(..., description="是否启用内存功能")
    storage_path: str = Field(..., description="内存存储文件路径")
    debounce_seconds: int = Field(..., description="内存更新的防抖时间（秒）")
    max_facts: int = Field(..., description="最大存储事实数量")
    fact_confidence_threshold: float = Field(..., description="事实的最低置信度阈值")
    injection_enabled: bool = Field(..., description="是否启用内存注入")
    max_injection_tokens: int = Field(..., description="内存注入的最大令牌数")


class MemoryStatusResponse(BaseModel):
    """内存状态的响应模型，包含配置与数据的综合信息。

    该模型用于表示内存系统的完整状态信息。

    Attributes:
        config: 内存系统配置。
        data: 内存数据。
    """

    config: MemoryConfigResponse
    data: MemoryResponse


@router.get(
    "/memory",
    response_model=MemoryResponse,
    summary="获取内存数据",
    description="检索当前全局内存数据，包括用户上下文、历史和事实。",
)
async def get_memory() -> MemoryResponse:
    """获取当前全局内存数据。

    从内存缓存中读取当前的内存数据，包括用户上下文、历史上下文和事实列表。

    Returns:
        MemoryResponse: 包含用户上下文、历史上下文和事实的当前内存数据。
    """
    memory_data = get_memory_data()
    return MemoryResponse(**memory_data)


@router.post(
    "/memory/reload",
    response_model=MemoryResponse,
    summary="重新加载内存数据",
    description="从存储文件重新加载内存数据，刷新内存缓存。",
)
async def reload_memory() -> MemoryResponse:
    """从存储文件重新加载内存数据。

    强制从存储文件重新加载内存数据，当文件被外部修改时非常有用。

    Returns:
        MemoryResponse: 重载后的内存数据。
    """
    memory_data = reload_memory_data()
    return MemoryResponse(**memory_data)


@router.get(
    "/memory/config",
    response_model=MemoryConfigResponse,
    summary="获取内存配置",
    description="检索当前内存系统的配置。",
)
async def get_memory_config_endpoint() -> MemoryConfigResponse:
    """获取内存系统的配置。

    Returns:
        MemoryConfigResponse: 当前内存配置设置。
    """
    config = get_memory_config()
    return MemoryConfigResponse(
        enabled=config.enabled,
        storage_path=config.storage_path,
        debounce_seconds=config.debounce_seconds,
        max_facts=config.max_facts,
        fact_confidence_threshold=config.fact_confidence_threshold,
        injection_enabled=config.injection_enabled,
        max_injection_tokens=config.max_injection_tokens,
    )


@router.get(
    "/memory/status",
    response_model=MemoryStatusResponse,
    summary="获取内存状态",
    description="在单个请求中检索内存配置和当前数据。",
)
async def get_memory_status() -> MemoryStatusResponse:
    """获取内存系统的状态信息，包含配置与当前数据。

    Returns:
        MemoryStatusResponse: 组合后的内存配置与当前数据。
    """
    config = get_memory_config()
    memory_data = get_memory_data()

    return MemoryStatusResponse(
        config=MemoryConfigResponse(
            enabled=config.enabled,
            storage_path=config.storage_path,
            debounce_seconds=config.debounce_seconds,
            max_facts=config.max_facts,
            fact_confidence_threshold=config.fact_confidence_threshold,
            injection_enabled=config.injection_enabled,
            max_injection_tokens=config.max_injection_tokens,
        ),
        data=MemoryResponse(**memory_data),
    )
