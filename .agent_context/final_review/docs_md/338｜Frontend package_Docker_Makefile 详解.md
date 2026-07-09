<title>338｜Frontend package/Docker/Makefile 详解</title>

<callout emoji="✅">
**本章目标：**补齐 remaining scripts/tests/routes/package docs 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| frontend/package.json | scripts/dependencies。 |
| frontend/Makefile | 前端命令封装。 |
| frontend/Dockerfile | 前端镜像。 |
| pnpm-lock.yaml | 依赖锁。 |
| next.config.js | Next 配置。 |

```mermaid
flowchart TD
  PackageJson --> PNPMInstall
  PackageJson --> Scripts
  Scripts --> Dev
  Scripts --> Build
  Scripts --> Test
  Dockerfile --> FrontendImage
  NextConfig --> Build
  PnpmLock --> PNPMInstall
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  Base["base node 22 alpine"]
  Base --> Pnpm["corepack pnpm 10.26.2"]
  Pnpm --> Copy["COPY frontend"]
  Copy --> Dev["dev stage"]
  Copy --> Builder["builder stage"]
  Dev --> DevInstall["pnpm install frozen-lockfile"]
  DevInstall --> DevRun["EXPOSE 3000 pnpm dev"]
  Builder --> BldInstall["pnpm install frozen-lockfile"]
  BldInstall --> BldBuild["SKIP_ENV_VALIDATION pnpm build"]
  BldBuild --> Prod["prod stage"]
  Prod --> ProdCopy["COPY frontend from builder"]
  ProdCopy --> ProdRun["CMD pnpm start"]
  MkStatic["Makefile build-static"] --> EnvCfg["NEXT_CONFIG_BUILD_OUTPUT standalone"]
  EnvCfg --> NextCfg["next.config.js"]
  NextCfg --> OutStd["output standalone"]
```