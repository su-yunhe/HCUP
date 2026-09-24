import { AppStorageV2 } from "@kit.ArkUI";
import { BreakpointRule, BreakpointType } from "./model/BreakpointModel";

/**
 * @file 全局断点状态，用于窗口尺寸响应式适配
 * @author Joker.X
 */

/**
 * AppStorageV2 键名
 */
export const BREAKPOINT_STATE_KEY: string = "breakpoint_state";

/**
 * 断点规则
 */
const BREAKPOINT_RULES: BreakpointRule[] = [
  /**
   * 超小断点
   */
  { name: BreakpointType.XS, maxWidthVp: 320 },
  /**
   * 小断点
   */
  { name: BreakpointType.SM, maxWidthVp: 600 },
  /**
   * 中断点
   */
  { name: BreakpointType.MD, maxWidthVp: 840 },
  /**
   * 大断点
   */
  { name: BreakpointType.LG, maxWidthVp: Number.POSITIVE_INFINITY }
];

/**
 * 全局断点状态
 */
@ObservedV2
export class BreakpointState {
  @Trace
  current: BreakpointType = BreakpointType.SM;
  @Trace
  windowWidthVp: number = 0;

  /**
   * 更新窗口宽度并计算断点
   * @param {number} windowWidthVp - 窗口宽度（vp）
   * @returns {void} 无返回值
   * @example
  * state.updateByWidth(360);
   */
  updateByWidth(windowWidthVp: number): void {
    this.windowWidthVp = windowWidthVp;
    const next = this.resolveBreakpoint(windowWidthVp);
    if (this.current !== next) {
      this.current = next;
    }
  }

  /**
   * 根据窗口宽度计算断点
   * @param {number} windowWidthVp - 窗口宽度（vp）
   * @returns {BreakpointType} 断点名称
   */
  resolveBreakpoint(windowWidthVp: number): BreakpointType {
    for (const rule of BREAKPOINT_RULES) {
      if (windowWidthVp < rule.maxWidthVp) {
        return rule.name;
      }
    }
    return BreakpointType.LG;
  }
}

/**
 * 获取全局断点状态实例；若不存在则创建
 * @returns {BreakpointState} 全局断点状态
 * @example
* const state = getBreakpointState();
 */
export function getBreakpointState(): BreakpointState {
  return AppStorageV2.connect<BreakpointState>(
    BreakpointState,
    BREAKPOINT_STATE_KEY,
    () => new BreakpointState()
  )!;
}
