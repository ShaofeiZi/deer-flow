/**
 * 【从 Markdown 文本中提取一级标题】
 *
 * 仅在内容以 "# " 开头时，提取首行作为标题，并移除 "# " 前缀与两侧空白。
 * 典型用于：根据 Markdown 内容生成会话/文档的默认标题。
 *
 * @param markdown - 【Markdown 原文】
 * @returns 【标题字符串】若不存在一级标题则返回 undefined。
 */
export function extractTitleFromMarkdown(markdown: string) {
  if (markdown.startsWith("# ")) {
    let title = markdown.split("\n")[0]!.trim();
    if (title.startsWith("# ")) {
      title = title.slice(2).trim();
    }
    return title;
  }
  return undefined;
}
