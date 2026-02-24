---
name: vercel-deploy
描述: 将应用程序和网站部署到 Vercel。当用户请求部署操作如"部署我的应用"、"部署到生产环境"、"创建预览部署"、"部署并给我链接"或"推送到线上"时使用此技能。无需认证 - 返回预览 URL 和可认领的部署链接。
metadata:
  author: vercel
  version: "1.0.0"
---

# Vercel 部署

即时将任何项目部署到 Vercel。无需认证。

## 工作原理

1. 将项目打包成 tarball（排除 `node_modules` 和 `.git`）
2. 从 `package.json` 自动检测框架
3. 上传到部署服务
4. 返回 **预览 URL**（实时站点）和 **认领 URL**（转移到您的 Vercel 账户）

## 用法

```bash
bash /mnt/skills/user/vercel-deploy/scripts/deploy.sh [path]
```

**参数：**
- `path` - 要部署的目录，或 `.tgz` 文件（默认为当前目录）

**示例：**

```bash
# 部署当前目录
bash /mnt/skills/user/vercel-deploy/scripts/deploy.sh

# 部署特定项目
bash /mnt/skills/user/vercel-deploy/scripts/deploy.sh /path/to/project

# 部署现有 tarball
bash /mnt/skills/user/vercel-deploy/scripts/deploy.sh /path/to/project.tgz
```

## 输出

```
Preparing deployment...
Detected framework: nextjs
Creating deployment package...
Deploying...
✓ Deployment successful!

Preview URL: https://skill-deploy-abc123.vercel.app
Claim URL:   https://vercel.com/claim-deployment?code=...
```

脚本还会向 stdout 输出 JSON 以供程序化使用：

```json
{
  "previewUrl": "https://skill-deploy-abc123.vercel.app",
  "claimUrl": "https://vercel.com/claim-deployment?code=...",
  "deploymentId": "dpl_...",
  "projectId": "prj_..."
}
```

## 框架检测

脚本从 `package.json` 自动检测框架。支持的框架包括：

- **React**：Next.js、Gatsby、Create React App、Remix、React Router
- **Vue**：Nuxt、Vitepress、Vuepress、Gridsome
- **Svelte**：SvelteKit、Svelte、Sapper
- **其他前端**：Astro、Solid Start、Angular、Ember、Preact、Docusaurus
- **后端**：Express、Hono、Fastify、NestJS、Elysia、h3、Nitro
- **构建工具**：Vite、Parcel
- **更多**：Blitz、Hydrogen、RedwoodJS、Storybook、Sanity 等

对于静态 HTML 项目（无 `package.json`），框架设置为 `null`。

## 静态 HTML 项目

对于没有 `package.json` 的项目：
- 如果有单个 `.html` 文件未命名为 `index.html`，它会自动重命名
- 这确保页面在根 URL（`/`）提供服务

## 向用户展示结果

始终显示两个 URL：

```
✓ 部署成功！

- [预览 URL](https://skill-deploy-abc123.vercel.app)
- [认领 URL](https://vercel.com/claim-deployment?code=...)

在预览 URL 查看您的站点。
要将此部署转移到您的 Vercel 账户，请访问认领 URL。
```

## 故障排除

### 网络出口错误

如果部署因网络限制失败（在 claude.ai 上常见），告诉用户：

```
部署因网络限制失败。要修复此问题：

1. 访问 https://claude.ai/settings/capabilities
2. 将 *.vercel.com 添加到允许的域名
3. 再次尝试部署
```
