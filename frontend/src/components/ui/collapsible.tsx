"use client";

import * as CollapsiblePrimitive from "@radix-ui/react-collapsible";

import { cn } from "@/lib/utils";

/**
 * 【组件功能描述】
 * 可折叠容器（Collapsible）根组件。
 *
 * - 基于 Radix Collapsible 的 Root 封装
 * - 用于控制内容区的展开/收起状态
 *
 * @param props - CollapsiblePrimitive.Root 的原生属性
 * @returns 可折叠根容器 JSX
 */
function Collapsible({
  ...props
}: React.ComponentProps<typeof CollapsiblePrimitive.Root>) {
  return <CollapsiblePrimitive.Root data-slot="collapsible" {...props} />;
}

/**
 * 【组件功能描述】
 * 可折叠触发器。
 *
 * - 基于 Radix CollapsibleTrigger 封装
 * - 用于点击切换展开/收起状态
 *
 * @param props - CollapsibleTrigger 的原生属性
 * @param props.className - 额外的 className
 * @returns 触发器 JSX
 */
function CollapsibleTrigger({
  className,
  ...props
}: React.ComponentProps<typeof CollapsiblePrimitive.CollapsibleTrigger>) {
  return (
    <CollapsiblePrimitive.CollapsibleTrigger
      data-slot="collapsible-trigger"
      className={cn("cursor-pointer", className)}
      {...props}
    />
  );
}

/**
 * 【组件功能描述】
 * 可折叠内容区域。
 *
 * - 基于 Radix CollapsibleContent 封装
 * - 随 Root 状态展开/收起
 *
 * @param props - CollapsibleContent 的原生属性
 * @returns 内容区域 JSX
 */
function CollapsibleContent({
  ...props
}: React.ComponentProps<typeof CollapsiblePrimitive.CollapsibleContent>) {
  return (
    <CollapsiblePrimitive.CollapsibleContent
      data-slot="collapsible-content"
      {...props}
    />
  );
}

export { Collapsible, CollapsibleTrigger, CollapsibleContent };
