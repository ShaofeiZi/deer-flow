"use client"

import * as React from "react"
import useEmblaCarousel, {
  type UseEmblaCarouselType,
} from "embla-carousel-react"
import { ArrowLeft, ArrowRight } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

/**
 * Embla Carousel 暴露的 API 类型别名。
 *
 * - 用于让外部通过 `setApi` 获取并控制轮播（例如：跳转、监听事件等）
 */
type CarouselApi = UseEmblaCarouselType[1]

/**
 * useEmblaCarousel 参数类型（options/plugins）的类型别名。
 *
 * - 便于在本文件内复用并对外导出关联类型
 */
type UseCarouselParameters = Parameters<typeof useEmblaCarousel>

/**
 * 轮播配置项类型（Embla options）。
 */
type CarouselOptions = UseCarouselParameters[0]

/**
 * 轮播插件类型（Embla plugins）。
 */
type CarouselPlugin = UseCarouselParameters[1]

/**
 * Carousel 组件对外 Props。
 */
type CarouselProps = {
  /** Embla 初始化配置（透传给 useEmblaCarousel 的 options） */
  opts?: CarouselOptions
  /** Embla 插件列表（透传给 useEmblaCarousel 的 plugins） */
  plugins?: CarouselPlugin
  /** 轮播方向：横向/纵向 */
  orientation?: "horizontal" | "vertical"
  /** 将 Embla API 暴露给外部调用方 */
  setApi?: (api: CarouselApi) => void
}

/**
 * Carousel Context 中保存的状态与操作集合。
 *
 * - 通过 Context 避免层层 props 传递
 * - 子组件（Content/Item/Prev/Next）可直接通过 useCarousel 访问
 */
type CarouselContextProps = {
  /** Embla 容器 ref（绑定到外层 viewport 节点） */
  carouselRef: ReturnType<typeof useEmblaCarousel>[0]
  /** Embla API 实例 */
  api: ReturnType<typeof useEmblaCarousel>[1]
  /** 向前滚动一页/一个步长 */
  scrollPrev: () => void
  /** 向后滚动一页/一个步长 */
  scrollNext: () => void
  /** 当前是否还能向前滚动 */
  canScrollPrev: boolean
  /** 当前是否还能向后滚动 */
  canScrollNext: boolean
} & CarouselProps

const CarouselContext = React.createContext<CarouselContextProps | null>(null)

/**
 * 【工具函数描述】
 * Carousel 的内部 Hook：从 Context 获取轮播状态与操作。
 *
 * - 仅允许在 <Carousel> 组件树内部使用
 * - 如果脱离 Provider 使用会抛错，帮助开发阶段快速定位问题
 *
 * @returns CarouselContextProps（轮播状态与操作集合）
 */
function useCarousel() {
  const context = React.useContext(CarouselContext)

  if (!context) {
    throw new Error("useCarousel must be used within a <Carousel />")
  }

  return context
}

/**
 * 【组件功能描述】
 * 轮播（Carousel）根组件。
 *
 * - 基于 Embla Carousel 实现滑动轮播
 * - 通过 Context 向子组件暴露 ref、api 以及上一页/下一页操作
 * - 支持键盘左右方向键控制（ArrowLeft/ArrowRight）
 *
 * @param props - 组件属性
 * @param props.orientation - 轮播方向：horizontal | vertical
 * @param props.opts - Embla options
 * @param props.plugins - Embla plugins
 * @param props.setApi - 将 Embla api 暴露给外部
 * @param props.className - 额外的 className
 * @returns Carousel 根容器 JSX
 */
function Carousel({
  orientation = "horizontal",
  opts,
  setApi,
  plugins,
  className,
  children,
  ...props
}: React.ComponentProps<"div"> & CarouselProps) {
  const [carouselRef, api] = useEmblaCarousel(
    {
      ...opts,
      axis: orientation === "horizontal" ? "x" : "y",
    },
    plugins
  )
  const [canScrollPrev, setCanScrollPrev] = React.useState(false)
  const [canScrollNext, setCanScrollNext] = React.useState(false)

  const onSelect = React.useCallback((api: CarouselApi) => {
    // 选择/重初始化时同步更新“可否滚动”状态
    if (!api) return
    setCanScrollPrev(api.canScrollPrev())
    setCanScrollNext(api.canScrollNext())
  }, [])

  const scrollPrev = React.useCallback(() => {
    // 向前滚动
    api?.scrollPrev()
  }, [api])

  const scrollNext = React.useCallback(() => {
    // 向后滚动
    api?.scrollNext()
  }, [api])

  const handleKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      // 仅处理方向键，避免影响其他快捷键
      if (event.key === "ArrowLeft") {
        event.preventDefault()
        scrollPrev()
      } else if (event.key === "ArrowRight") {
        event.preventDefault()
        scrollNext()
      }
    },
    [scrollPrev, scrollNext]
  )

  React.useEffect(() => {
    // 将 api 回传给外部调用方（若提供 setApi）
    if (!api || !setApi) return
    setApi(api)
  }, [api, setApi])

  React.useEffect(() => {
    // 绑定 Embla 事件：初始化/选择变更
    if (!api) return
    onSelect(api)
    api.on("reInit", onSelect)
    api.on("select", onSelect)

    return () => {
      api?.off("select", onSelect)
    }
  }, [api, onSelect])

  return (
    <CarouselContext.Provider
      value={{
        carouselRef,
        api: api,
        opts,
        orientation:
          orientation || (opts?.axis === "y" ? "vertical" : "horizontal"),
        scrollPrev,
        scrollNext,
        canScrollPrev,
        canScrollNext,
      }}
    >
      <div
        onKeyDownCapture={handleKeyDown}
        className={cn("relative", className)}
        role="region"
        aria-roledescription="carousel"
        data-slot="carousel"
        {...props}
      >
        {children}
      </div>
    </CarouselContext.Provider>
  )
}

/**
 * 【组件功能描述】
 * 轮播内容区域（viewport + container）。
 *
 * - 外层绑定 Embla ref（viewport）
 * - 内层为 flex 容器，横向/纵向布局由 orientation 决定
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 轮播内容区域 JSX
 */
function CarouselContent({ className, ...props }: React.ComponentProps<"div">) {
  const { carouselRef, orientation } = useCarousel()

  return (
    <div
      ref={carouselRef}
      className="overflow-hidden"
      data-slot="carousel-content"
    >
      <div
        className={cn(
          "flex",
          orientation === "horizontal" ? "-ml-4" : "-mt-4 flex-col",
          className
        )}
        {...props}
      />
    </div>
  )
}

/**
 * 【组件功能描述】
 * 轮播单页（slide）容器。
 *
 * - 每个 CarouselItem 对应一个 slide
 * - 通过 padding 与 CarouselContent 的负 margin 配合实现间距
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 单页容器 JSX
 */
function CarouselItem({ className, ...props }: React.ComponentProps<"div">) {
  const { orientation } = useCarousel()

  return (
    <div
      role="group"
      aria-roledescription="slide"
      data-slot="carousel-item"
      className={cn(
        "min-w-0 shrink-0 grow-0 basis-full",
        orientation === "horizontal" ? "pl-4" : "pt-4",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 上一页按钮。
 *
 * - 基于通用 Button 组件
 * - 自动根据 canScrollPrev 禁用
 * - 根据 orientation 定位在左右或上下
 *
 * @param props - Button 组件属性
 * @param props.className - 额外的 className
 * @returns 上一页按钮 JSX
 */
function CarouselPrevious({
  className,
  variant = "outline",
  size = "icon",
  ...props
}: React.ComponentProps<typeof Button>) {
  const { orientation, scrollPrev, canScrollPrev } = useCarousel()

  return (
    <Button
      data-slot="carousel-previous"
      variant={variant}
      size={size}
      className={cn(
        "absolute size-8 rounded-full",
        orientation === "horizontal"
          ? "top-1/2 -left-12 -translate-y-1/2"
          : "-top-12 left-1/2 -translate-x-1/2 rotate-90",
        className
      )}
      disabled={!canScrollPrev}
      onClick={scrollPrev}
      {...props}
    >
      <ArrowLeft />
      <span className="sr-only">Previous slide</span>
    </Button>
  )
}

/**
 * 【组件功能描述】
 * 下一页按钮。
 *
 * - 基于通用 Button 组件
 * - 自动根据 canScrollNext 禁用
 * - 根据 orientation 定位在左右或上下
 *
 * @param props - Button 组件属性
 * @param props.className - 额外的 className
 * @returns 下一页按钮 JSX
 */
function CarouselNext({
  className,
  variant = "outline",
  size = "icon",
  ...props
}: React.ComponentProps<typeof Button>) {
  const { orientation, scrollNext, canScrollNext } = useCarousel()

  return (
    <Button
      data-slot="carousel-next"
      variant={variant}
      size={size}
      className={cn(
        "absolute size-8 rounded-full",
        orientation === "horizontal"
          ? "top-1/2 -right-12 -translate-y-1/2"
          : "-bottom-12 left-1/2 -translate-x-1/2 rotate-90",
        className
      )}
      disabled={!canScrollNext}
      onClick={scrollNext}
      {...props}
    >
      <ArrowRight />
      <span className="sr-only">Next slide</span>
    </Button>
  )
}

export {
  type CarouselApi,
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
}
