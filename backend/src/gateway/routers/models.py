from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.config import get_app_config

router = APIRouter(prefix="/api", tags=["models"])


class ModelResponse(BaseModel):
    """技能模型信息的响应模型。

    该模型用于表示单个 AI 模型的详细信息，包括名称、显示名称、
    描述以及是否支持思考模式等属性。

    Attributes:
        name: 模型的唯一标识符。
        display_name: 模型的可读名称。
        description: 模型描述。
        supports_thinking: 模型是否支持思考模式。
    """

    name: str = Field(..., description="模型的唯一标识符")
    display_name: str | None = Field(None, description="模型的可读名称")
    description: str | None = Field(None, description="模型描述")
    supports_thinking: bool = Field(default=False, description="模型是否支持思考模式")


class ModelsListResponse(BaseModel):
    """列出所有模型的响应模型。

    该模型用于表示模型列表的响应结构。

    Attributes:
        models: 模型响应对象列表。
    """

    models: list[ModelResponse]


@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="列出所有模型",
    description="检索系统中配置的所有可用 AI 模型列表。",
)
async def list_models() -> ModelsListResponse:
    """列出系统中所有可用的模型及其元数据。

    从应用配置中获取所有已配置的模型信息，并返回模型列表。

    Returns:
        ModelsListResponse: 包含所有模型列表的响应对象。
    """
    config = get_app_config()
    models = [
        ModelResponse(
            name=model.name,
            display_name=model.display_name,
            description=model.description,
            supports_thinking=model.supports_thinking,
        )
        for model in config.models
    ]
    return ModelsListResponse(models=models)


@router.get(
    "/models/{model_name}",
    response_model=ModelResponse,
    summary="获取模型详情",
    description="按名称检索特定 AI 模型的详细信息。",
)
async def get_model(model_name: str) -> ModelResponse:
    """按名称检索特定模型的详细信息。

    根据模型名称查找并返回该模型的详细配置信息。

    Args:
        model_name: 要获取的模型名称。

    Returns:
        ModelResponse: 模型详细信息响应对象。

    Raises:
        HTTPException: 模型不存在时抛出 404 错误。
    """
    config = get_app_config()
    model = config.get_model_config(model_name)
    if model is None:
        raise HTTPException(status_code=404, detail=f"未找到模型 '{model_name}'")

    return ModelResponse(
        name=model.name,
        display_name=model.display_name,
        description=model.description,
        supports_thinking=model.supports_thinking,
    )
