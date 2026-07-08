{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 84｜Jina、DDG、InfoQuest Provider 单模块详解\n\n<callout emoji=\"✅\">\n**本章目标：**细化 Jina fetch、DDG search、InfoQuest 多能力 provider。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Jina | 异步 web_fetch，支持 timeout/proxy 参数清洗。 |\n| DDG | DuckDuckGo 文本搜索，自动推断 region 和 Wikipedia 后端。 |\n| InfoQuest | web_search/web_fetch/image_search 三合一。 |\n| Image Search | 图片搜索结果用于多媒体任务。 |\n\n```mermaid\nflowchart TD\n  Input[query or url] --> Provider{provider}\n  Provider --> Jina[JinaClient fetch]\n  Provider --> DDG[DDGS text search]\n  Provider --> Info[InfoQuestClient]\n  Info --> InfoSearch[web search]\n  Info --> InfoFetch[web fetch]\n  Info --> InfoImage[image search]\n  Jina --> Output[normalized output]\n  DDG --> Output\n  InfoSearch --> Output\n  InfoFetch --> Output\n  InfoImage --> Output\n```",
      "document_id": "CLtTdACCIoOmyLxUHpOmPenGyzL",
      "revision_id": 18
    }
  }
}
