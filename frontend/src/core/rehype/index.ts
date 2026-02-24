import type { Element, Root, ElementContent } from "hast";
import { useMemo } from "react";
import { visit } from "unist-util-visit";
import type { BuildVisitor } from "unist-util-visit";

/**
 * 【Rehype 插件：将文本按“词/字”拆分为 span】
 *
 * 用途：为 Markdown 渲染后的文本提供逐词/逐字动画能力。
 * 实现思路：
 * - 遍历 AST 中指定的文本容器节点（p / 标题 / 列表 / strong 等）
 * - 将纯文本子节点按 `Intl.Segmenter`（中文分词，granularity=word）切分
 * - 每个 segment 用一个 <span class="animate-fade-in"> 包裹，方便在 CSS/动画层逐段展示
 *
 * @returns 【rehype transformer】传入 Root 并原地改写其 children。
 */
export function rehypeSplitWordsIntoSpans() {
  return (tree: Root) => {
    visit(tree, "element", ((node: Element) => {
      if (
        ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "strong"].includes(
          node.tagName,
        ) &&
        node.children
      ) {
        const newChildren: Array<ElementContent> = [];
        node.children.forEach((child) => {
          if (child.type === "text") {
            const segmenter = new Intl.Segmenter("zh", { granularity: "word" });
            const segments = segmenter.segment(child.value);
            const words = Array.from(segments)
              .map((segment) => segment.segment)
              .filter(Boolean);
            words.forEach((word: string) => {
              newChildren.push({
                type: "element",
                tagName: "span",
                properties: {
                  className: "animate-fade-in",
                },
                children: [{ type: "text", value: word }],
              });
            });
          } else {
            newChildren.push(child);
          }
        });
        node.children = newChildren;
      }
    }) as BuildVisitor<Root, "element">);
  };
}

/**
 * 【Hook：按需启用 rehypeSplitWordsIntoSpans】
 *
 * 使用方式：
 * ```ts
 * const rehypePlugins = useRehypeSplitWordsIntoSpans(enabled);
 * <Streamdown rehypePlugins={rehypePlugins} />
 * ```
 *
 * 说明：
 * - 当 enabled=false 时返回空数组，避免无意义的 AST 遍历。
 * - 通过 useMemo 缓存数组引用，减少渲染组件的无效更新。
 *
 * @param enabled - 【是否启用】默认 true。
 * @returns 【rehypePlugins 数组】可直接传给支持 rehypePlugins 的渲染组件。
 */
export function useRehypeSplitWordsIntoSpans(enabled = true) {
  const rehypePlugins = useMemo(
    () => (enabled ? [rehypeSplitWordsIntoSpans] : []),
    [enabled],
  );
  return rehypePlugins;
}
