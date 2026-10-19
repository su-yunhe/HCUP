import { Song, SongClass } from '../common/entities/SongsResult';
import { changeDuration } from '../common/functions/functions';
import { pauseMusic, resumeMusic, seekMusic } from '../common/functions/playerControl';
import AudioPlayUtils from '../common/utils/AudioPlayUtils';

/**
 * 全屏播放页
 */
@Entry
@Component
struct PlayPage {
  @StorageProp('topRectHeight') topRectHeight: number = 0
  @StorageProp('bottomRectHeight') bottomRectHeight: number = 0
  @StorageProp('player-mode') playmode: number = 1
  @StorageProp('player-fileName') fileName: string = ''
  @StorageProp('player-song') song: Song = SongClass
  @StorageProp('player-artists') artists: string = ''
  @StorageProp('player-ispaused') isPaused: boolean = false
  @StorageProp('player-picurl') picUrl: string = ''
  @StorageProp('player-time') time: number = 0

  @State isDragging: boolean = false // 拖动期间进度条不跟随播放进度
  @State dragValue: number = 0
  private isClosing: boolean = false // 防止连点收起多次返回

  // 进度条总长：优先用歌曲信息时长，本地文件没有歌曲信息时用播放器时长
  getMaxDuration(): number {
    if (this.song.duration > 0) { return this.song.duration }
    return this.time >= 0 ? AudioPlayUtils.mPlayer.duration : 0
  }

  getSliderValue(): number {
    const value = this.isDragging ? this.dragValue : this.time
    return Math.max(0, Math.min(value, this.getMaxDuration()))
  }

  close() {
    if (this.isClosing) { return }
    this.isClosing = true
    this.getUIContext().getRouter().back()
  }

  onBackPress(): boolean | void {
    if (this.isClosing) { return true }
    this.isClosing = true
  }

  build() {
    Column() {
      // 顶部：向下箭头收起（居中放置，连点时多余的点击不会落到下层页面的返回按钮上）
      Row() {
        Button({ type: ButtonType.Circle }) {
          Image($r('app.media.ic_public_back'))
            .width(25)
            .fillColor($r('app.color.reverse'))
            .rotate({ angle: -90 })
        }
        .id('play_page_down')
        .accessibilityText('向下箭头')
        .accessibilityDescription('向下箭头')
        .width(44)
        .height(44)
        .backgroundColor(Color.Transparent)
        .onClick(() => { this.close() })
      }
      .width('100%')
      .justifyContent(FlexAlign.Center)
      .padding({ left: 10, right: 10 })

      // 封面、歌名、歌手
      Column({ space: 15 }) {
        Image(this.playmode == 1 && this.picUrl && this.picUrl != 'NULL' ?
          this.picUrl + '?param=512y512' : $r('app.media.ic_music_fill'))
          .id('play_page_cover')
          .width('75%')
          .aspectRatio(1)
          .borderRadius(10)
          .backgroundColor($r('app.color.background'))
          .fillColor($r('app.color.reverse'))
        Text(this.playmode == 0 ? this.fileName : this.song.name)
          .id('play_page_title')
          .textStyle(24)
          .fontWeight(FontWeight.Bold)
          .padding({ top: 20 })
        Text(this.artists)
          .id('play_page_artist')
          .textStyle(16)
          .opacity(0.7)
      }
      .width('100%')
      .layoutWeight(1)
      .justifyContent(FlexAlign.Center)
      .padding({ left: 30, right: 30 })

      // 进度条
      Column() {
        Slider({ value: this.getSliderValue(), min: 0, max: this.getMaxDuration(), style: SliderStyle.OutSet })
          .id('play_page_slider')
          .width('100%')
          .onChange((value: number, mode: SliderChangeMode) => {
            if (mode == SliderChangeMode.Begin || mode == SliderChangeMode.Moving) {
              this.isDragging = true
              this.dragValue = value
            } else if (mode == SliderChangeMode.End || mode == SliderChangeMode.Click) {
              this.dragValue = value
              this.isDragging = false
              seekMusic(value)
            }
          })
        Row() {
          Text(changeDuration(this.getSliderValue()))
            .id('play_page_current_time')
            .fontSize(14)
            .fontColor($r('app.color.reverse'))
          Text(changeDuration(this.getMaxDuration()))
            .id('play_page_duration')
            .fontSize(14)
            .fontColor($r('app.color.reverse'))
        }
        .width('100%')
        .justifyContent(FlexAlign.SpaceBetween)
        .padding({ left: 10, right: 10 })
      }
      .width('100%')
      .padding({ left: 20, right: 20 })

      // 暂停、继续
      Row() {
        if (!this.isPaused) {
          Button({ type: ButtonType.Circle }) {
            Image($r('app.media.ic_public_pause')).width(40).fillColor($r('app.color.reverse'))
          }
          .id('play_page_pause_btn')
          .width(72)
          .height(72)
          .backgroundColor(Color.Transparent)
          .onClick(() => { pauseMusic() })
        } else {
          Button({ type: ButtonType.Circle }) {
            Image($r('app.media.ic_play_fill')).width(40).fillColor($r('app.color.reverse'))
          }
          .id('play_page_play_btn')
          .width(72)
          .height(72)
          .backgroundColor(Color.Transparent)
          .onClick(() => { resumeMusic() })
        }
      }
      .width('100%')
      .justifyContent(FlexAlign.Center)
      .padding({ top: 20, bottom: 40 })
    }
    .id('play_page')
    .width('100%')
    .height('100%')
    .padding({
      top: this.getUIContext().px2vp(this.topRectHeight),
      bottom: this.getUIContext().px2vp(this.bottomRectHeight)
    })
    .backgroundColor($r('app.color.main'))
  }
}

@Extend(Text) function textStyle(size: number) {
  .fontSize(size)
  .fontColor($r('app.color.reverse'))
  .maxLines(1)
  .textOverflow({ overflow: TextOverflow.Ellipsis })
}
