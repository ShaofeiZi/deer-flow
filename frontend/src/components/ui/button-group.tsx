import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"
import { Separator } from "@/components/ui/separator"

/**
 * ButtonGroup 组件的样式变体集合。
 *
 * - 通过 `orientation` 控制横向/纵向排列
 * - 内置处理子元素圆角、边框拼接、focus-visible 层级等细节
 */
const buttonGroupVariants = cva(
  "flex w-fit items-stretch [&>*]:focus-visible:z-10 [&>*]:focus-visible:relative [&>[data-slot=select-trigger]:not([class*='w-'])]:w-fit [&>input]:flex-1 has-[select[aria-hidden=true]:last-child]:[&>[data-slot=select-trigger]:last-of-type]:rounded-r-md has-[>[data-slot=button-group]]:gap-2",
  {
    variants: {
      orientation: {
        horizontal:
          "[&>*:not(:first-child)]:rounded-l-none [&>*:not(:first-child)]:border-l-0 [&>*:not(:last-child)]:rounded-r-none",
        vertical:
          "flex-col [&>*:not(:first-child)]:rounded-t-none [&>*:not(:first-child)]:border-t-0 [&>*:not(:last-child)]:rounded-b-none",
      },
    },
    defaultVariants: {
      orientation: "horizontal",
    },
  }
)

/**
 * 【组件功能描述】
 * 按钮组容器组件。
 *
 * - 用于将多个按钮/输入/选择器以一组形式展示
 * - 统一控制边框拼接与圆角，让多个控件看起来像一个整体
 *
 * @param props - 组件属性
 * @param props.className - 额外的 className
 * @param props.orientation - 排列方向：horizontal | vertical
 * @returns 按钮组容器 JSX
 */
function ButtonGroup({
  className,
  orientation,
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof buttonGroupVariants>) {
  return (
    <div
      role="group"
      data-slot="button-group"
      data-orientation={orientation}
      className={cn(buttonGroupVariants({ orientation }), className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 按钮组的文本/静态内容块。
 *
 * - 常用于在按钮组中插入不可点击的说明文字或图标+文字组合
 * - 支持 `asChild` 将样式透传给子元素
 *
 * @param props - 组件属性
 * @param props.className - 额外的 className
 * @param props.asChild - 是否使用 Slot 让子元素作为实际渲染节点
 * @returns 文本块 JSX
 */
function ButtonGroupText({
  className,
  asChild = false,
  ...props
}: React.ComponentProps<"div"> & {
  asChild?: boolean
}) {
  const Comp = asChild ? Slot : "div"

  return (
    <Comp
      className={cn(
        "bg-muted flex items-center gap-2 rounded-md border px-4 text-sm font-medium shadow-xs [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 按钮组分隔线。
 *
 * - 基于通用 Separator 组件封装
 * - 默认使用纵向分隔（orientation = "vertical"），适配横向按钮组
 *
 * @param props - Separator 组件属性
 * @param props.className - 额外的 className
 * @param props.orientation - 分隔线方向
 * @returns 分隔线 JSX
 */
function ButtonGroupSeparator({
  className,
  orientation = "vertical",
  ...props
}: React.ComponentProps<typeof Separator>) {
  return (
    <Separator
      data-slot="button-group-separator"
      orientation={orientation}
      className={cn(
        "bg-input relative !m-0 self-stretch data-[orientation=vertical]:h-auto",
        className
      )}
      {...props}
    />
  )
}

export {
  ButtonGroup,
  ButtonGroupSeparator,
  ButtonGroupText,
  buttonGroupVariants,
}
