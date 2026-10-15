/**
 * 歌词样式
 */
export interface LyricStyle {
  size: number
  color: ResourceColor | string
  align: 'center' | 'start'
  mode: number // 0 - Normal, 1 - Translate, 2 - Roma
  enabled: boolean // 是否启用浮动歌词
  widthRatio: number // 悬浮窗宽度占屏幕宽度比例 0~1
  opacity: number // 悬浮窗整体透明度 0~1
  positionX: number // 悬浮窗左上角x比例 0~1
  positionY: number // 悬浮窗左上角y比例 0~1，-1 表示未设置过，使用默认顶部避让位置
  backgroundBlur: boolean // 是否开启背景模糊
}

/**
 * 缓存设置
 */
export interface CacheSet {
  songCacheMaxSize: number
  staticCacheMaxSize: number
}

export const CacheSetItem: CacheSet = {
  songCacheMaxSize: 1024 * 1024 * 1024,
  staticCacheMaxSize: 1024 * 1024 * 1024
}

export const LyricStyleItem: LyricStyle = {
  size: 20,
  color: Color.White,
  align: 'center',
  mode: 0,
  enabled: true,
  widthRatio: 0.8,
  opacity: 1,
  positionX: 0.1,
  positionY: -1,
  backgroundBlur: true,
}

/**
 * 浅拷贝 LyricStyle，避免多处 @StorageProp 共享同一对象引用导致互相覆盖。
 * ArkTS 不支持用展开运算符构造对象字面量（arkts-no-spread），故逐字段拷贝。
 */
export function cloneLyricStyle(style: LyricStyle): LyricStyle {
  return {
    size: style.size,
    color: style.color,
    align: style.align,
    mode: style.mode,
    enabled: style.enabled,
    widthRatio: style.widthRatio,
    opacity: style.opacity,
    positionX: style.positionX,
    positionY: style.positionY,
    backgroundBlur: style.backgroundBlur,
  }
}