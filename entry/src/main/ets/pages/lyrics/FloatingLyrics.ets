import { StorageConstants } from "../../common/constants/StorageConstants"
import { display, window } from "@kit.ArkUI"
import Constants from "../../common/constants/Constants";
import { LyricStyle, LyricStyleItem, cloneLyricStyle } from "../../common/entities/local/Settings";
import { changeSettings } from "../../common/functions/app/settings";

interface Position {
  x: number,
  y: number
}

const TAG = "FloatingLyrics";
const DisplayW = display.getDefaultDisplaySync().width;
const DisplayH = display.getDefaultDisplaySync().height;
const BOTTOM_MARGIN = vp2px(60);

@Entry
@Component
export struct FloatingLyrics {
  @StorageProp(StorageConstants.CURRENT_LYRIC) currentLyric: string = '';
  @StorageProp(StorageConstants.PLAY_ARTISTS) artists: string = '';
  @StorageProp(StorageConstants.LYRIC_STYLE) lyricStyle: LyricStyle = LyricStyleItem;
  @State @Watch("moveWindow") windowPosition: Position = { x: 0, y: 0 };
  private panOption: PanGestureOptions = new PanGestureOptions({ direction: PanDirection.All });
  private win: window.Window | null = null;
  private winWidth: number = 0;

  aboutToAppear(): void {
    this.win = window.findWindow(Constants.FLOAT_LYRICS_WIN_NAME);
    this.win.setWindowBackgroundColor("#00000000") // transparent
    this.win.setWindowFocusable(false);
    this.winWidth = this.win.getGlobalRect().width;
  }

  moveWindow() {
    this.win?.moveWindowTo(this.windowPosition.x, this.windowPosition.y);
  }

  private persistPosition() {
    const latest = AppStorage.get<LyricStyle>(StorageConstants.LYRIC_STYLE) ?? this.lyricStyle;
    const style: LyricStyle = cloneLyricStyle(latest);
    style.positionX = this.windowPosition.x / DisplayW;
    style.positionY = this.windowPosition.y / DisplayH;
    changeSettings(StorageConstants.LYRIC_STYLE, style);
  }

  build() {
    Stack() {
      Stack({alignContent: this.lyricStyle.align === 'center' ? Alignment.Center : Alignment.Start}) {
        Text(this.currentLyric)
          .textStyle(this.lyricStyle.size, this.lyricStyle.align === 'center' ? TextAlign.Center : TextAlign.Start)
          .textOverflow({ overflow: TextOverflow.MARQUEE })
          .fontColor(Color.Gray)
      }
      .padding({left: 10})
      .width('80%')
      .height('100%')
      .backgroundBlurStyle(this.lyricStyle.backgroundBlur ? BlurStyle.Thick : BlurStyle.NONE)
      .backgroundColor(this.lyricStyle.backgroundBlur ? Color.Transparent : 'rgba(0,0,0,0.35)')
      .borderRadius(16)
    }
    .opacity(this.lyricStyle.opacity)
    .parallelGesture(GestureGroup(GestureMode.Exclusive,
      TapGesture({ count: 2, fingers: 1 })
        .onAction(() => {
          this.win?.destroyWindow();
        }),
      PanGesture(this.panOption)
        .onActionStart((event: GestureEvent) => {
          if (!this.win) {
            return;
          }
          this.windowPosition.x = this.win!.getGlobalRect().left;
          this.windowPosition.y = this.win!.getGlobalRect().top;
        })
        .onActionUpdate((event: GestureEvent) => {
          let resX = this.windowPosition.x + event.offsetX;
          let resY = this.windowPosition.y + event.offsetY;
          if (resX < 0 || resX + this.winWidth > DisplayW) {
            resX = this.windowPosition.x;
          }
          if (resY < Constants.FLOAT_LYRICS_TOP_MARGIN || resY >  DisplayH - BOTTOM_MARGIN) {
            resY = this.windowPosition.y;
          }
          this.windowPosition = { x: resX, y: resY };
        })
        .onActionEnd((event: GestureEvent) => {
          this.persistPosition();
        })
    ))
    .width('100%')
    .height('100%')
    .backgroundColor(Color.Transparent)
  }
}

@Extend(Text) function textStyle(size: number, align: TextAlign) {
  .fontSize(size)
  .fontColor($r('app.color.reverse'))
  .textAlign(align)
  .layoutWeight(1)
  .width('100%')
  .maxLines(1)
  .padding({ left: 10, right: 10 })
  .textOverflow({ overflow: TextOverflow.Ellipsis })
}
