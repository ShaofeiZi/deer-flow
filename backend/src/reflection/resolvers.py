from importlib import import_module
from typing import TypeVar

T = TypeVar("T")


def resolve_variable[T](
    variable_path: str,
    expected_type: type[T] | tuple[type, ...] | None = None,
) -> T:
    """从路径解析变量。

    Args:
        variable_path: 变量的路径（例如 "parent_package_name.sub_package_name.module_name:variable_name"）。
        expected_type: 可选的类型或类型元组，用于验证解析后的变量。
            如果提供，使用 isinstance() 检查变量是否为预期类型的实例。

    Returns:
        解析后的变量。

    Raises:
        ImportError: 如果模块路径无效或属性不存在。
        ValueError: 如果解析后的变量未通过验证检查。
    """
    try:
        module_path, variable_name = variable_path.rsplit(":", 1)
    except ValueError as err:
        raise ImportError(f"{variable_path} 不是有效的变量路径。示例：parent_package_name.sub_package_name.module_name:variable_name") from err

    try:
        module = import_module(module_path)
    except ImportError as err:
        raise ImportError(f"无法导入模块 {module_path}") from err

    try:
        variable = getattr(module, variable_name)
    except AttributeError as err:
        raise ImportError(f"模块 {module_path} 未定义 {variable_name} 属性/类") from err

    # 类型验证
    if expected_type is not None:
        if not isinstance(variable, expected_type):
            type_name = expected_type.__name__ if isinstance(expected_type, type) else " 或 ".join(t.__name__ for t in expected_type)
            raise ValueError(f"{variable_path} 不是 {type_name} 的实例，实际为 {type(variable).__name__}")

    return variable


def resolve_class[T](class_path: str, base_class: type[T] | None = None) -> type[T]:
    """从模块路径和类名解析类。

    Args:
        class_path: 类的路径（例如 "langchain_openai:ChatOpenAI"）。
        base_class: 基类，用于检查解析后的类是否为其子类。

    Returns:
        解析后的类。

    Raises:
        ImportError: 如果模块路径无效或属性不存在。
        ValueError: 如果解析后的对象不是类或不是 base_class 的子类。
    """
    model_class = resolve_variable(class_path, expected_type=type)

    if not isinstance(model_class, type):
        raise ValueError(f"{class_path} 不是有效的类")

    if base_class is not None and not issubclass(model_class, base_class):
        raise ValueError(f"{class_path} 不是 {base_class.__name__} 的子类")

    return model_class
