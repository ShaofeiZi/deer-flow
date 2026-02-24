import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import type { StreamdownProps } from "streamdown";

import { rehypeSplitWordsIntoSpans } from "../rehype";

/**
 * 【Streamdown 渲染插件配置（默认）】
 *
 * - remarkPlugins：Markdown 解析阶段插件（GFM、数学公式等）
 * - rehypePlugins：HTML AST 处理阶段插件（raw HTML、KaTeX 渲染等）
 *
 * 主要用于 AI/系统消息等需要支持 GFM + 数学公式 + raw HTML 的渲染场景。
 */
export const streamdownPlugins = {
  remarkPlugins: [
    remarkGfm,
    [remarkMath, { singleDollarTextMath: true }],
  ] as StreamdownProps["remarkPlugins"],
  rehypePlugins: [
    rehypeRaw,
    [rehypeKatex, { output: "html" }],
  ] as StreamdownProps["rehypePlugins"],
};

/**
 * 【Streamdown 渲染插件配置（逐词动画）】
 *
 * 在默认 KaTeX 支持的基础上，额外启用 `rehypeSplitWordsIntoSpans`：
 * - 将可动画的文本节点拆分为多个 <span>，便于在 UI 层做逐字/逐词淡入效果。
 *
 * 注意：该配置刻意不包含 `rehypeRaw`，以避免 raw HTML 与拆分逻辑的交互复杂度。
 */
export const streamdownPluginsWithWordAnimation = {
  remarkPlugins: [
    remarkGfm,
    [remarkMath, { singleDollarTextMath: true }],
  ] as StreamdownProps["remarkPlugins"],
  rehypePlugins: [
    [rehypeKatex, { output: "html" }],
    rehypeSplitWordsIntoSpans,
  ] as StreamdownProps["rehypePlugins"],
};

// Plugins for human messages - no autolink to prevent URL bleeding into adjacent text
/**
 * 【人类消息渲染插件配置】
 *
 * 目标：避免 remark-gfm 的“自动链接识别”把 URL 黏连到相邻文本（URL bleeding），
 * 因此不启用 `remarkGfm`，仅保留数学公式解析。
 */
export const humanMessagePlugins = {
  remarkPlugins: [
    // Use remark-gfm without autolink literals by not including it
    // Only include math support for human messages
    [remarkMath, { singleDollarTextMath: true }],
  ] as StreamdownProps["remarkPlugins"],
  rehypePlugins: [
    [rehypeKatex, { output: "html" }],
  ] as StreamdownProps["rehypePlugins"],
};
