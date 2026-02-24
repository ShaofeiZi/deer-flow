from pydantic import BaseModel, ConfigDict, Field


class VolumeMountConfig(BaseModel):
    """卷挂载配置。

    该类用于配置主机与容器之间的目录挂载。

    Attributes:
        host_path: 主机上的路径。
        container_path: 容器内的路径。
        read_only: 挂载是否为只读。
    """

    host_path: str = Field(..., description="主机上的路径")
    container_path: str = Field(..., description="容器内的路径")
    read_only: bool = Field(default=False, description="挂载是否为只读")


class SandboxConfig(BaseModel):
    """沙箱配置。

    该类用于配置沙箱环境的各项参数，包括提供者类路径、Docker 镜像、
    端口、容器前缀、空闲超时、卷挂载和环境变量等。

    通用选项：
        use: 沙箱提供者的类路径（必需）

    AioSandboxProvider 特定选项：
        image: 使用的 Docker 镜像（默认：enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest）
        port: 沙箱容器的基础端口（默认：8080）
        base_url: 如果设置，使用现有沙箱而非启动新容器
        auto_start: 是否自动启动 Docker 容器（默认：true）
        container_prefix: 容器名称前缀（默认：deer-flow-sandbox）
        idle_timeout: 沙箱释放前的空闲超时秒数（默认：600 = 10 分钟）。设置为 0 以禁用。
        mounts: 与容器共享目录的卷挂载列表
        environment: 注入到容器中的环境变量（以 $ 开头的值从主机环境变量解析）

    Attributes:
        use: 沙箱提供者的类路径。
        image: 沙箱容器使用的 Docker 镜像。
        port: 沙箱容器的基础端口。
        base_url: 现有沙箱的 URL（如果设置则使用现有沙箱）。
        auto_start: 是否自动启动 Docker 容器。
        container_prefix: 容器名称前缀。
        idle_timeout: 沙箱释放前的空闲超时秒数。
        mounts: 卷挂载列表。
        environment: 注入到沙箱容器的环境变量。
    """

    use: str = Field(
        ...,
        description="沙箱提供者的类路径（例如 src.sandbox.local:LocalSandboxProvider）",
    )
    image: str | None = Field(
        default=None,
        description="沙箱容器使用的 Docker 镜像",
    )
    port: int | None = Field(
        default=None,
        description="沙箱容器的基础端口",
    )
    base_url: str | None = Field(
        default=None,
        description="如果设置，使用此 URL 的现有沙箱而非启动新容器",
    )
    auto_start: bool | None = Field(
        default=None,
        description="是否自动启动 Docker 容器",
    )
    container_prefix: str | None = Field(
        default=None,
        description="容器名称前缀",
    )
    idle_timeout: int | None = Field(
        default=None,
        description="沙箱释放前的空闲超时秒数（默认：600 = 10 分钟）。设置为 0 以禁用。",
    )
    mounts: list[VolumeMountConfig] = Field(
        default_factory=list,
        description="主机与容器之间共享目录的卷挂载列表",
    )
    environment: dict[str, str] = Field(
        default_factory=dict,
        description="注入到沙箱容器的环境变量。以 $ 开头的值将从主机环境变量解析。",
    )

    model_config = ConfigDict(extra="allow")
