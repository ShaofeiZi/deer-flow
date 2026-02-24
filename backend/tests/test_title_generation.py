"""自动线程标题生成的测试。"""

import pytest

from src.agents.middlewares.title_middleware import TitleMiddleware
from src.config.title_config import TitleConfig, get_title_config, set_title_config


class TestTitleConfig:
    """TitleConfig 的测试类。"""

    def test_default_config(self):
        """测试默认配置值。"""
        config = TitleConfig()
        assert config.enabled is True
        assert config.max_words == 6
        assert config.max_chars == 60
        assert config.model_name is None

    def test_custom_config(self):
        """测试自定义配置。"""
        config = TitleConfig(
            enabled=False,
            max_words=10,
            max_chars=100,
            model_name="gpt-4",
        )
        assert config.enabled is False
        assert config.max_words == 10
        assert config.max_chars == 100
        assert config.model_name == "gpt-4"

    def test_config_validation(self):
        """测试配置验证。"""
        # max_words 应在 1 到 20 之间
        with pytest.raises(ValueError):
            TitleConfig(max_words=0)
        with pytest.raises(ValueError):
            TitleConfig(max_words=21)

        # max_chars 应在 10 到 200 之间
        with pytest.raises(ValueError):
            TitleConfig(max_chars=5)
        with pytest.raises(ValueError):
            TitleConfig(max_chars=201)

    def test_get_set_config(self):
        """测试全局配置的获取和设置。"""
        original_config = get_title_config()

        # 设置新配置
        new_config = TitleConfig(enabled=False, max_words=10)
        set_title_config(new_config)

        # 验证已设置
        assert get_title_config().enabled is False
        assert get_title_config().max_words == 10

        # 恢复原始配置
        set_title_config(original_config)


class TestTitleMiddleware:
    """TitleMiddleware 的测试类。"""

    def test_middleware_initialization(self):
        """测试中间件可以初始化。"""
        middleware = TitleMiddleware()
        assert middleware is not None
        assert middleware.state_schema is not None

    # TODO: 使用模拟 Runtime 添加集成测试
    # def test_should_generate_title(self):
    #     """测试标题生成触发逻辑。"""
    #     pass

    # def test_generate_title(self):
    #     """测试标题生成。"""
    #     pass

    # def test_after_agent_hook(self):
    #     """测试 after_agent 钩子。"""
    #     pass


# TODO: 添加集成测试
# - 使用真实 LangGraph runtime 测试
# - 使用 checkpointer 测试标题持久化
# - 测试 LLM 失败时的回退行为
# - 测试并发标题生成
