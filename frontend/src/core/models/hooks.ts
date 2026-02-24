import { useQuery } from "@tanstack/react-query";

import { loadModels } from "./api";

/**
 * 【Hook：获取模型列表（带缓存/加载状态）】
 *
 * 基于 TanStack Query：
 * - 自动缓存模型列表（queryKey=["models"]）
 * - 暴露加载态与错误信息
 * - 可通过 enabled 控制是否发起请求
 *
 * 使用示例：
 * ```ts
 * const { models, isLoading, error } = useModels({ enabled: true });
 * ```
 *
 * @param options - 【可选配置】
 * @param options.enabled - 【是否启用查询】默认 true。
 * @returns 【查询结果】包含 models / isLoading / error。
 */
export function useModels({ enabled = true }: { enabled?: boolean } = {}) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["models"],
    queryFn: () => loadModels(),
    enabled,
  });
  return { models: data ?? [], isLoading, error };
}
