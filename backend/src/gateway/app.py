"""DeerFlow Gateway FastAPI 应用入口。

本模块负责创建 Gateway API 的 FastAPI 应用实例，并注册各业务路由（models / mcp / memory / skills / artifacts / uploads）。

说明：
- Gateway 是独立进程，向前端提供 REST API。
- LangGraph Server 通过 nginx 反向代理（/api/langgraph/*），与 Gateway 分离。
- MCP 工具的初始化不在此处进行：MCP tools 由 LangGraph Server 的 Agents 使用，且两者缓存独立。"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.gateway.config import get_gateway_config
from src.gateway.routers import artifacts, mcp, memory, models, skills, uploads

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期（lifespan）处理器。

    Args:
        app: FastAPI 应用实例（由框架注入）。

    Yields:
        None
    """
    config = get_gateway_config()
    logger.info(f"Starting API Gateway on {config.host}:{config.port}")

    # 注意：这里不初始化 MCP tools，原因：
    # 1) Gateway 本身不直接使用 MCP tools，它们由 LangGraph Server 中的 Agents 使用。
    # 2) Gateway 与 LangGraph Server 是两个独立进程，缓存互不共享。
    # 因此 MCP tools 会在 LangGraph Server 侧首次需要时再延迟初始化。

    yield
    logger.info("Shutting down API Gateway")


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用。

    Returns:
        已完成配置与路由注册的 FastAPI 应用实例。
    """

    app = FastAPI(
        title="DeerFlow API Gateway",
        description="""
## DeerFlow API Gateway

DeerFlow 的 API Gateway：基于 LangGraph 的 AI Agent 后端（含 sandbox 执行能力）的配套 REST API。

### 功能

- **Models Management**：查询并获取可用 AI 模型列表
- **MCP Configuration**：管理 Model Context Protocol (MCP) server 配置
- **Memory Management**：读取/刷新全局 memory 数据，用于个性化对话
- **Skills Management**：查询与管理 skills 及其启用状态
- **Artifacts**：访问 thread 产出的 artifacts / 文件
- **Health Monitoring**：健康检查接口

### 架构

LangGraph 相关请求由 nginx 反向代理处理；
本 Gateway 提供 models、MCP、skills、artifacts、uploads 等自定义端点。
        """,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "models",
                "description": "Operations for querying available AI models and their configurations",
            },
            {
                "name": "mcp",
                "description": "Manage Model Context Protocol (MCP) server configurations",
            },
            {
                "name": "memory",
                "description": "Access and manage global memory data for personalized conversations",
            },
            {
                "name": "skills",
                "description": "Manage skills and their configurations",
            },
            {
                "name": "artifacts",
                "description": "Access and download thread artifacts and generated files",
            },
            {
                "name": "uploads",
                "description": "Upload and manage user files for threads",
            },
            {
                "name": "health",
                "description": "Health check and system status endpoints",
            },
        ],
    )

    # CORS is handled by nginx - no need for FastAPI middleware

    # Include routers
    # Models API is mounted at /api/models
    app.include_router(models.router)

    # MCP API is mounted at /api/mcp
    app.include_router(mcp.router)

    # Memory API is mounted at /api/memory
    app.include_router(memory.router)

    # Skills API is mounted at /api/skills
    app.include_router(skills.router)

    # Artifacts API is mounted at /api/threads/{thread_id}/artifacts
    app.include_router(artifacts.router)

    # Uploads API is mounted at /api/threads/{thread_id}/uploads
    app.include_router(uploads.router)

    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """健康检查接口。

        Returns:
            服务健康状态信息。
        """
        return {"status": "healthy", "service": "deer-flow-gateway"}

    return app


# Create app instance for uvicorn
app = create_app()
