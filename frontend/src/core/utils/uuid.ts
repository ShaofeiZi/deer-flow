/**
 * 【UUID 工具函数出口】
 *
 * 直接复用 `uuid` 包的 v4 实现，并以项目统一的命名导出 `uuid`，
 * 便于在各处生成随机 UUID。
 */
export { v4 as uuid } from "uuid";
