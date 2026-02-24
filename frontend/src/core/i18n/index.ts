export { enUS } from "./locales/en-US";
export { zhCN } from "./locales/zh-CN";
export type { Translations } from "./locales/types";

/**
 * 【应用支持的语言标识】
 *
 * 用于：
 * - i18n 文案选择
 * - 日期/时间等本地化展示
 */
export type Locale = "en-US" | "zh-CN";

// Helper function to detect browser locale
/**
 * 【自动检测浏览器语言】
 *
 * - 浏览器端：读取 `navigator.language`（或旧版 `userLanguage`）
 * - 服务端/构建期：无法访问 window/navigator，默认返回 "en-US"
 *
 * 目前策略：
 * - 只要语言以 "zh" 开头（zh/zh-CN/zh-TW 等）就判定为中文。
 * - 其它情况统一回退到英文。
 *
 * @returns 【Locale】应用内部语言枚举值。
 */
export function detectLocale(): Locale {
  if (typeof window === "undefined") {
    return "en-US";
  }

  const browserLang =
    navigator.language ||
    (navigator as unknown as { userLanguage: string }).userLanguage;

  // Check if browser language is Chinese (zh, zh-CN, zh-TW, etc.)
  if (browserLang.toLowerCase().startsWith("zh")) {
    return "zh-CN";
  }

  return "en-US";
}
