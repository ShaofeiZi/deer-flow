import { parse } from "best-effort-json-parser";

/**
 * 【尽力解析 JSON 字符串】
 *
 * 与原生 `JSON.parse` 不同，`best-effort-json-parser` 会尝试处理一些“接近 JSON”的输入，
 * 例如模型输出中常见的轻微格式问题（多余逗号、未严格转义等）。
 *
 * @param json - 【待解析字符串】可能为严格或非严格 JSON。
 * @returns 【解析结果】成功返回对象/数组/基础类型，失败返回 undefined。
 */
export function tryParseJSON(json: string) {
  try {
    const object = parse(json);
    return object;
  } catch {
    return undefined;
  }
}
