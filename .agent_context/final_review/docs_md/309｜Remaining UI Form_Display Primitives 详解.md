<title>309｜Remaining UI Form/Display Primitives 详解</title>

<callout emoji="✅">
**本章目标：**补齐剩余 frontend/UI/misc 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| carousel.tsx | 轮播组件。 |
| progress.tsx | 进度展示。 |
| separator.tsx | 分隔线。 |
| skeleton.tsx | 骨架屏。 |
| terminal.tsx | 终端展示。 |
| number-ticker.tsx | 数字动效。 |

```mermaid
flowchart TD
  Data --> NumberTicker
  Loading --> Skeleton
  Logs --> Terminal
  Wizard --> Progress
  Layout --> Separator
  Landing --> Carousel
  Components --> AppUI
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
stateDiagram-v2
  [*] --> NotInView : Terminal mounts
  NotInView --> InView : useInView fires
  InView --> ItemActive : sequenceStarted and activeIndex equals itemIndex
  ItemActive --> ItemComplete : AnimatedSpan onAnimationComplete
  ItemActive --> ItemComplete : TypingAnimation interval ends
  ItemComplete --> ItemActive : completeItem sets activeIndex+1
  ItemComplete --> Done : last child completed
  Done --> [*]
```