"use client";

import { useEffect } from "react";

import { useI18nContext } from "./context";
import { getLocaleFromCookie, setLocaleInCookie } from "./cookies";
import { enUS } from "./locales/en-US";
import { zhCN } from "./locales/zh-CN";

import { detectLocale, type Locale, type Translations } from "./index";

/**
 * 【内置翻译表】
 *
 * 将 Locale 映射到对应的翻译资源对象（Translations）。
 * `useI18n` 会根据当前 locale 从这里取出 `t`。
 */
const translations: Record<Locale, Translations> = {
  "en-US": enUS,
  "zh-CN": zhCN,
};

/**
 * 【Hook：i18n 状态与翻译文本访问】
 *
 * 该 Hook 提供：
 * - `locale`：当前语言
 * - `t`：当前语言对应的翻译文本对象
 * - `changeLocale(newLocale)`：切换语言（同时写入 cookie 持久化）
 *
 * 使用示例：
 * ```ts
 * const { locale, t, changeLocale } = useI18n();
 * console.log(t.common.settings);
 * changeLocale("zh-CN");
 * ```
 *
 * 初始化逻辑：组件挂载时若 cookie 中不存在 locale，则自动检测浏览器语言并写入 cookie。
 *
 * @returns 【i18n 能力集合】包含 locale / t / changeLocale。
 */
export function useI18n() {
  const { locale, setLocale } = useI18nContext();

  const t = translations[locale];

  /**
   * 【切换语言】
   *
   * 同步更新：
   * - React Context 中的 locale 状态
   * - cookie 中的持久化值（用于下次访问/刷新后保持语言）
   *
   * @param newLocale - 【目标语言】必须是应用支持的 Locale。
   */
  const changeLocale = (newLocale: Locale) => {
    setLocale(newLocale);
    setLocaleInCookie(newLocale);
  };

  // Initialize locale on mount
  useEffect(() => {
    const saved = getLocaleFromCookie() as Locale | null;
    if (!saved) {
      const detected = detectLocale();
      setLocale(detected);
      setLocaleInCookie(detected);
    }
  }, [setLocale]);

  return {
    locale,
    t,
    changeLocale,
  };
}
