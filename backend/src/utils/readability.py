import re
from urllib.parse import urljoin

from markdownify import markdownify as md
from readabilipy import simple_json_from_html_string


class Article:
    """表示从网页提取的文章内容。

    该类用于存储文章的标题和 HTML 内容，并提供转换为
    Markdown 格式和消息格式的方法。

    Attributes:
        url: 文章的 URL 地址。
        title: 文章标题。
        html_content: 文章的 HTML 内容。
    """

    url: str

    def __init__(self, title: str, html_content: str):
        """初始化文章对象。

        Args:
            title: 文章标题。
            html_content: 文章的 HTML 内容。
        """
        self.title = title
        self.html_content = html_content

    def to_markdown(self, including_title: bool = True) -> str:
        """将文章内容转换为 Markdown 格式。

        Args:
            including_title: 是否在 Markdown 中包含标题，默认为 True。

        Returns:
            转换后的 Markdown 字符串。
        """
        markdown = ""
        if including_title:
            markdown += f"# {self.title}\n\n"

        if self.html_content is None or not str(self.html_content).strip():
            markdown += "*无可用内容*\n"
        else:
            markdown += md(self.html_content)

        return markdown

    def to_message(self) -> list[dict]:
        """将文章内容转换为消息格式，用于 AI 模型输入。

        将 Markdown 内容解析为文本和图像的混合内容列表，
        图像会被转换为 image_url 格式。

        Returns:
            包含文本和图像内容的字典列表。
        """
        image_pattern = r"!\[.*?\]\((.*?)\)"

        content: list[dict[str, str]] = []
        markdown = self.to_markdown()

        if not markdown or not markdown.strip():
            return [{"type": "text", "text": "无可用内容"}]

        parts = re.split(image_pattern, markdown)

        for i, part in enumerate(parts):
            if i % 2 == 1:
                image_url = urljoin(self.url, part.strip())
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            else:
                text_part = part.strip()
                if text_part:
                    content.append({"type": "text", "text": text_part})

        # 如果处理完所有部分后内容仍为空，提供回退消息
        if not content:
            content = [{"type": "text", "text": "无可用内容"}]

        return content


class ReadabilityExtractor:
    """使用 Readability 算法从网页提取文章内容。

    该类使用 readabilipy 库从 HTML 中提取主要文章内容，
    去除广告、导航栏等无关内容。
    """

    def extract_article(self, html: str) -> Article:
        """从 HTML 内容中提取文章。

        Args:
            html: 网页的 HTML 内容。

        Returns:
            包含标题和内容的 Article 对象。
        """
        article = simple_json_from_html_string(html, use_readability=True)

        html_content = article.get("content")
        if not html_content or not str(html_content).strip():
            html_content = "无法从此页面提取内容"

        title = article.get("title")
        if not title or not str(title).strip():
            title = "无标题"

        return Article(title=title, html_content=html_content)
