import logging

from langchain.chat_models import BaseChatModel

from src.config import get_app_config, get_tracing_config, is_tracing_enabled
from src.reflection import resolve_class

logger = logging.getLogger(__name__)


def create_chat_model(name: str | None = None, thinking_enabled: bool = False, **kwargs) -> BaseChatModel:
    """从配置创建聊天模型实例。

    Args:
        name: 要创建的模型名称。如果为 None，将使用配置中的第一个模型。
        thinking_enabled: 是否启用思考模式。

    Returns:
        聊天模型实例。
    """
    config = get_app_config()
    if name is None:
        name = config.models[0].name
    model_config = config.get_model_config(name)
    if model_config is None:
        raise ValueError(f"配置中未找到模型 {name}") from None

    if model_config.custom_endpoint:
        from src.models.custom_endpoint import CustomEndpointChatOpenAI

        model_class = CustomEndpointChatOpenAI
    else:
        model_class = resolve_class(model_config.use, BaseChatModel)

    model_settings_from_config = model_config.model_dump(
        exclude_none=True,
        exclude={
            "use",
            "name",
            "display_name",
            "description",
            "supports_thinking",
            "when_thinking_enabled",
            "supports_vision",
            "custom_endpoint",
        },
    )
    if thinking_enabled and model_config.when_thinking_enabled is not None:
        if not model_config.supports_thinking:
            raise ValueError(f"模型 {name} 不支持思考模式。在 `config.yaml` 中将 `supports_thinking` 设置为 true 以启用思考模式。") from None
        model_settings_from_config.update(model_config.when_thinking_enabled)

    if model_config.custom_endpoint:
        model_settings_from_config["custom_endpoint"] = model_config.custom_endpoint

    model_instance = model_class(**kwargs, **model_settings_from_config)

    if is_tracing_enabled():
        try:
            from langchain_core.tracers.langchain import LangChainTracer

            tracing_config = get_tracing_config()
            tracer = LangChainTracer(
                project_name=tracing_config.project,
            )
            existing_callbacks = model_instance.callbacks or []
            model_instance.callbacks = [*existing_callbacks, tracer]
            logger.debug(
                f"LangSmith 追踪已附加到模型 '{name}'（项目='{tracing_config.project}'）"
            )
        except Exception as e:
            logger.warning(f"无法将 LangSmith 追踪附加到模型 '{name}'：{e}")
    return model_instance
