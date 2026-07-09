<title>117｜UI Visual Effects Primitives：MagicBento、Aurora、Shine、Spotlight 详解</title>

<callout emoji="✅">
**本章目标：**继续按小模块解释职责、输入输出和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| magic-bento.tsx | 视觉卡片效果。 |
| aurora-text.tsx | 渐变文字。 |
| shine-border.tsx | 发光边框。 |
| spotlight-card.tsx | 聚光卡片。 |
| flickering-grid.tsx | 闪烁网格背景。 |
| word-rotate/number-ticker | 动态文字/数字。 |

```mermaid
flowchart TD
  Landing --> MagicBento
  Landing --> AuroraText
  Cards --> ShineBorder
  Cards --> SpotlightCard
  AuthPages --> FlickeringGrid
  Metrics --> NumberTicker
  Headlines --> WordRotate
  VisualPrimitives --> BrandExperience
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart TD
  MB["MagicBento"]
  UMD["useMobileDetection"]
  GS["GlobalSpotlight"]
  BCG["BentoCardGrid"]
  Stars{"enableStars"}
  PC["ParticleCard"]
  Plain["plain bento-card div"]
  Glow["--glow-intensity"]
  Parts["particle clones"]
  Tilt["rotateX rotateY"]
  Mag["magnet x y"]
  Ripple["click ripple"]
  GSAP["gsap tweens"]

  MB --> UMD
  MB --> GS
  MB --> BCG
  MB --> Stars
  UMD -->|"shouldDisableAnimations"| GS
  UMD -->|"shouldDisableAnimations"| PC
  Stars -->|true| PC
  Stars -->|false| Plain
  BCG --> PC
  GS --> Glow
  PC --> Parts
  PC --> Tilt
  PC --> Mag
  PC --> Ripple
  Parts --> GSAP
  Tilt --> GSAP
  Mag --> GSAP
  Ripple --> GSAP
```