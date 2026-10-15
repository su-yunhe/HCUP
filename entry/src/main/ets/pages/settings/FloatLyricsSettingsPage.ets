import Constants from "../../common/constants/Constants"
import { StorageConstants } from "../../common/constants/StorageConstants"
import { LyricStyle, LyricStyleItem, cloneLyricStyle } from "../../common/entities/local/Settings"
import { changeSettings } from "../../common/functions/app/settings"
import { display, window } from "@kit.ArkUI"

/**
 * 浮动歌词设置详情页
 */
@Component
export struct FloatLyricsSettingsPage {
  @StorageProp(StorageConstants.LYRIC_STYLE) lyricStyle: LyricStyle = LyricStyleItem
  @State style: LyricStyle = LyricStyleItem

  aboutToAppear(): void {
    this.style = cloneLyricStyle(this.lyricStyle)
  }

  private updateLyricStyle() {
    this.lyricStyle = cloneLyricStyle(this.style)
    changeSettings(StorageConstants.LYRIC_STYLE, this.lyricStyle)
  }

  /**
   * “启用浮动歌词”作为悬浮窗开关总闸：关闭时若悬浮窗已创建则销毁；
   * 悬浮窗未创建（window.findWindow 抛出异常）时无需处理。
   */
  private applyEnabledState(isOn: boolean) {
    if (isOn) {
      return
    }
    try {
      const win: window.Window = window.findWindow(Constants.FLOAT_LYRICS_WIN_NAME)
      win.destroyWindow()
    } catch (e) {
      // 悬浮窗未创建时无需处理
    }
  }

  /**
   * 悬浮窗已创建时，位置比例变化需实时联动窗口坐标；
   * 悬浮窗未创建（window.findWindow 抛出异常）时仅保留持久化，不强制创建窗口。
   */
  private syncFloatWindowPosition() {
    try {
      const win: window.Window = window.findWindow(Constants.FLOAT_LYRICS_WIN_NAME)
      const displayW = display.getDefaultDisplaySync().width
      const displayH = display.getDefaultDisplaySync().height
      const posX = Math.round(displayW * this.style.positionX)
      const posY = this.style.positionY < 0
        ? Constants.FLOAT_LYRICS_TOP_MARGIN
        : Math.round(displayH * this.style.positionY)
      win.moveWindowTo(posX, posY)
    } catch (e) {
      // 悬浮窗未创建时忽略实时联动，仅保留持久化
    }
  }

  build() {
    NavDestination() {
      Scroll() {
        Column({ space: 20 }) {
          this.SwitchRow($r('app.string.FLOATLYRICS_ENABLE'), this.style.enabled, (isOn: boolean) => {
            this.style.enabled = isOn
            this.updateLyricStyle()
            this.applyEnabledState(isOn)
          })

          this.SwitchRow($r('app.string.FLOATLYRICS_CENTER'), this.style.align === 'center', (isOn: boolean) => {
            this.style.align = isOn ? 'center' : 'start'
            this.updateLyricStyle()
          })

          this.SliderRow($r('app.string.FLOATLYRICS_FONTSIZE'), this.style.size, 10, 30, (value: number) => {
            this.style.size = value
            this.updateLyricStyle()
          })

          this.SliderRow($r('app.string.FLOATLYRICS_WIDTH'), this.style.widthRatio, 0.4, 1, (value: number) => {
            this.style.widthRatio = value
            this.updateLyricStyle()
          })

          this.SliderRow($r('app.string.FLOATLYRICS_OPACITY'), this.style.opacity, 0.2, 1, (value: number) => {
            this.style.opacity = value
            this.updateLyricStyle()
          })

          this.SliderRow($r('app.string.FLOATLYRICS_POSITION_X'), this.style.positionX, 0, 1, (value: number) => {
            this.style.positionX = value
            this.updateLyricStyle()
            this.syncFloatWindowPosition()
          })

          this.SliderRow($r('app.string.FLOATLYRICS_POSITION_Y'),
            this.style.positionY < 0 ? 0 : this.style.positionY, 0, 1, (value: number) => {
            this.style.positionY = value
            this.updateLyricStyle()
            this.syncFloatWindowPosition()
          })

          this.SwitchRow($r('app.string.FLOATLYRICS_BLUR'), this.style.backgroundBlur, (isOn: boolean) => {
            this.style.backgroundBlur = isOn
            this.updateLyricStyle()
          })
        }
        .padding(Constants.PADDING_EDGE_DEFAULT)
      }
      .scrollBar(BarState.Off)
      .width('100%')
      .height('100%')
    }
    .title($r('app.string.SET_FLOATLYRICS'))
    .backgroundColor($r('app.color.background'))
  }

  @Builder SwitchRow(title: ResourceStr, isOn: boolean, onChange: (isOn: boolean) => void) {
    Row() {
      Text(title)
        .fontSize(Constants.FONT_SIZE_COMMON)
        .fontWeight(FontWeight.Bold)
      Toggle({ type: ToggleType.Switch, isOn: isOn })
        .height(24)
        .width(48)
        .onChange(onChange)
        .selectedColor($r('app.color.app_red'))
    }
    .height(Constants.HEIGHT_SETTINGS_ITEM)
    .width('100%')
    .justifyContent(FlexAlign.SpaceBetween)
    .padding({ left: Constants.PADDING_EDGE_DEFAULT, right: Constants.PADDING_EDGE_DEFAULT })
    .rowItemStyle()
  }

  @Builder SliderRow(title: ResourceStr, value: number, min: number, max: number, onChange: (value: number) => void) {
    Column({ space: 5 }) {
      Row() {
        Text(title)
          .fontSize(Constants.FONT_SIZE_COMMON)
          .fontWeight(FontWeight.Bold)
        Text(value.toFixed(2))
          .fontSize(Constants.FONT_SIZE_COMMON)
          .fontWeight(FontWeight.Bold)
      }
      .width('100%')
      .justifyContent(FlexAlign.SpaceBetween)

      Slider({ value: value, min: min, max: max })
        .selectedColor($r('app.color.app_red'))
        .width('100%')
        .onChange((val: number, mode: SliderChangeMode) => {
          onChange(val)
        })
    }
    .width('100%')
    .padding({ left: Constants.PADDING_EDGE_DEFAULT, right: Constants.PADDING_EDGE_DEFAULT, top: 10, bottom: 10 })
    .rowItemStyle()
  }

  @Styles rowItemStyle() {
    .backgroundColor($r('app.color.main'))
    .borderRadius(Constants.RADIUS_CARD)
  }
}
