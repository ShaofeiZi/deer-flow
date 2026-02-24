import { getBackendBaseURL } from "../config";

import type { Model } from "./types";

/**
 * 【加载可用模型列表】
 *
 * 从后端接口获取当前实例配置的可用模型，用于前端模型选择与能力展示。
 *
 * @returns 【模型数组】后端返回的 models 字段。
 */
export async function loadModels() {
  const res = fetch(`${getBackendBaseURL()}/api/models`);
  const { models } = (await (await res).json()) as { models: Model[] };
  return models;
}
