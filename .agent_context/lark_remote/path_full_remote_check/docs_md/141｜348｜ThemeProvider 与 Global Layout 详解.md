{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 348｜ThemeProvider 与 Global Layout 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化前端 UI/Landing/I18n 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| theme-provider.tsx | next-themes wrapper。 |\n| app/layout.tsx | RootLayout。 |\n| globals.css | 全局样式。 |\n| body/html | 主题和 hydration 设置。 |\n\n```mermaid\nflowchart TD\n  RootLayout --> HTML\n  HTML --> Body\n  Body --> ThemeProvider\n  ThemeProvider --> I18nProvider\n  I18nProvider --> AppChildren\n  GlobalsCSS --> Body\n  ThemeToggle --> ThemeProvider\n```",
      "document_id": "K08idKcD1oq7cbxeH3smCGTryod",
      "revision_id": 18
    }
  }
}
