import { Sentence } from '../model/Sentence';
import { ThemeConst } from 'constants';

/**
 * 名句内容 + 出处，关联诗词时在其后展示"查看原文"入口
 */
@ComponentV2
export struct SentenceView {
  @Param @Require sentence: Sentence;
  @Param poemId: number | null = null;
  @Event viewOriginal: (poemId: number) => void = (poemId: number) => {
  };

  build() {
    Column() {
      // 生成图片时截取该卡片
      Column({ space: 16 }) {
        Text(this.sentence.content)
          .id('sentence_content')
          .width('100%')
          .fontSize(20)
          .lineHeight(32)
        Text(this.sentence.from)
          .id('sentence_from')
          .width('100%')
          .textAlign(TextAlign.End)
          .fontSize(ThemeConst.FontSize_14)
          .fontColor(ThemeConst.FontColor_BlockTitle)
      }
      .id('sentence_card')
      .width('100%')
      .padding(24)
      .backgroundColor(ThemeConst.BackGroundColor_Normal)

      if (this.poemId !== null) {
        Text('查看原文')
          .id('sentence_view_original')
          .fontColor('#ff007dff')
          .padding(ThemeConst.P_X16_Y8)
          .onClick(() => {
            this.viewOriginal(this.poemId as number)
          })
      }
    }
    .width('100%')
    .alignItems(HorizontalAlign.End)
  }
}
