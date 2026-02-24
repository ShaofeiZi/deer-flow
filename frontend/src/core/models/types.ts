/**
 * 【模型信息】
 *
 * 描述可用大模型的基础元数据，用于：
 * - 模型选择器展示
 * - 判断是否支持“思考模式”等能力
 */
export interface Model {
  /**
   * 【模型唯一标识】通常用于后端路由/调用参数。
   */
  id: string;
  /**
   * 【模型内部名称】例如供应商原始名称或配置名称。
   */
  name: string;
  /**
   * 【展示名称】面向用户 UI 展示的名称。
   */
  display_name: string;
  /**
   * 【模型描述】可选，用于 UI 提示。
   */
  description?: string | null;
  /**
   * 【是否支持思考/推理模式】可选。
   */
  supports_thinking?: boolean;
}
