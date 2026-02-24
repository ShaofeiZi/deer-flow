import { formatDistanceToNow } from "date-fns";
import { enUS as dateFnsEnUS, zhCN as dateFnsZhCN } from "date-fns/locale";

import { detectLocale, type Locale } from "@/core/i18n";
import { getLocaleFromCookie } from "@/core/i18n/cookies";

/**
 * 【将应用 Locale 映射为 date-fns 的 Locale】
 *
 * date-fns 的 `formatDistanceToNow` 等 API 需要传入对应的语言包对象。
 * 这里根据应用内部的 Locale 值，选择 date-fns 提供的 locale 实现。
 *
 * @param locale - 【应用内部 Locale】例如 "zh-CN" / "en-US"。
 * @returns 【date-fns Locale 对象】用于日期格式化与相对时间计算。
 */
function getDateFnsLocale(locale: Locale) {
  switch (locale) {
    case "zh-CN":
      return dateFnsZhCN;
    case "en-US":
    default:
      return dateFnsEnUS;
  }
}

/**
 * 【格式化“距今时间”文本】
 *
 * 基于 date-fns 的 `formatDistanceToNow` 生成类似：
 * - 中文："3 分钟前"、"大约 1 小时前"
 * - 英文："3 minutes ago"、"about 1 hour ago"
 *
 * Locale 选择优先级：
 * 1) 显式传入的 `locale`
 * 2) Cookie 中保存的语言
 * 3) 自动检测（首屏/无 Cookie 的兜底）
 *
 * @param date - 【目标时间】支持 Date / ISO 字符串 / 时间戳。
 * @param locale - 【可选语言】不传则按 cookie/自动检测决定。
 * @returns 【相对时间字符串】带后缀（ago/前）。
 */
export function formatTimeAgo(date: Date | string | number, locale?: Locale) {
  const effectiveLocale =
    locale ??
    (getLocaleFromCookie() as Locale | null) ??
    // Fallback when cookie is missing (or on first render)
    detectLocale();
  return formatDistanceToNow(date, {
    addSuffix: true,
    locale: getDateFnsLocale(effectiveLocale),
  });
}
