import { ThemeConst } from 'constants';
import { BoldTitle } from 'uicomponents';
import { Idiom, IdiomExample, IdiomQuote, IdiomSource, readIdiomIdsByWords } from '../model/Idiom';

@ComponentV2
export struct IdiomView {
  @Param @Require idiom: Idiom;
  @Event onOpenIdiom: (id: number) => void = () => {
  };
  @Local linkedIds: Map<string, number> = new Map();

  aboutToAppear(): void {
    this.loadLinks()
  }

  @Monitor('idiom')
  onIdiomChange() {
    this.linkedIds = new Map()
    this.loadLinks()
  }

  loadLinks() {
    const words: string[] = relatedWords(this.idiom)
    if (words.length === 0) {
      return
    }
    readIdiomIdsByWords(words).then((ids: Map<string, number>) => {
      this.linkedIds = ids
    })
  }

  build() {
    Column() {
      Text(this.idiom.word)
        .id('idiom_word')
        .width('100%')
        .padding(ThemeConst.P_X16_Y8)
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
      Text(this.idiom.pinyin)
        .id('idiom_pinyin')
        .width('100%')
        .padding(ThemeConst.P_X16_Y8)
        .fontSize(14)
        .fontColor(Color.Gray)
      BoldTitle({ text: '释义' })
      Text(this.idiom.explanation ?? '暂无')
        .id('idiom_explanation')
        .width('100%')
        .padding(ThemeConst.P_X16_Y8)
        .lineHeight(24)
      BoldTitle({ text: '出处' })
      Text(parseSource(this.idiom.source))
        .id('idiom_source')
        .width('100%')
        .padding(ThemeConst.P_X16_Y8)
        .lineHeight(24)
      BoldTitle({ text: '例句' })
      Text(parseExample(this.idiom.example, this.idiom.word))
        .id('idiom_example')
        .width('100%')
        .padding(ThemeConst.P_X16_Y8)
        .lineHeight(24)
      if (this.idiom.usage) {
        BoldTitle({ text: '用法' })
        Text(this.idiom.usage)
          .width('100%')
          .padding(ThemeConst.P_X16_Y8)
          .lineHeight(24)
      }
      if (this.idiom.quote) {
        BoldTitle({ text: '名著引用' })
        Text(parseQuote(this.idiom.quote))
          .width('100%')
          .padding(ThemeConst.P_X16_Y8)
          .lineHeight(24)
      }
      if (this.idiom.story && this.idiom.story.length > 0) {
        BoldTitle({ text: '成语故事' })
        ForEach(this.idiom.story, (item: string) => {
          Text(item)
            .width('100%')
            .padding(ThemeConst.P_X16_Y8)
            .lineHeight(24)
        })
      }
      if (this.idiom.notice) {
        BoldTitle({ text: '注意' })
        Text(this.idiom.notice)
          .width('100%')
          .padding(ThemeConst.P_X16_Y8)
          .lineHeight(24)
      }
      if (this.idiom.similar && this.idiom.similar.length > 0) {
        BoldTitle({ text: '近义词' })
        this.WordTags(this.idiom.similar)
      }
      if (this.idiom.opposite && this.idiom.opposite.length > 0) {
        BoldTitle({ text: '反义词' })
        this.WordTags(this.idiom.opposite)
      }
    }
    .width('100%')
    .alignItems(HorizontalAlign.Start)
  }

  @Builder
  WordTags(words: string[]) {
    Flex({ wrap: FlexWrap.Wrap }) {
      ForEach(words, (word: string) => {
        Text(word)
          .id(`idiom_tag_${word}`)
          .padding({
            left: 12,
            top: 6,
            right: 12,
            bottom: 6
          })
          .margin({ right: 8, bottom: 8 })
          .borderRadius(14)
          .borderWidth(1)
          .borderColor(this.linkedIds.has(word) ? '#ff3d6dd8' : '#ffc9cdd2')
          .fontColor(this.linkedIds.has(word) ? '#ff3d6dd8' : Color.Gray)
          .fontSize(ThemeConst.FontSize_14)
          .onClick(() => {
            const id = this.linkedIds.get(word)
            if (id !== undefined && id > 0) {
              this.onOpenIdiom(id)
            } else {
              this.getUIContext().getPromptAction().showToast({ message: `词库中暂未收录「${word}」` })
            }
          })
      })
    }
    .width('100%')
    .padding({ left: 16, right: 16, bottom: 8 })
  }
}

function relatedWords(idiom: Idiom): string[] {
  const words: string[] = []
  const append = (list: string[] | null) => {
    if (!list) {
      return
    }
    list.forEach((word: string) => {
      if (word.length > 0 && !words.includes(word)) {
        words.push(word)
      }
    })
  }
  append(idiom.similar)
  append(idiom.opposite)

  return words
}

function parseSource(source: IdiomSource | null): string {
  if (!source) {
    return '暂无'
  }
  let text = source.text ?? ''
  if (source.book) {
    text += text.length > 0 ? ` ——${source.book}` : source.book
  }

  return text.length > 0 ? text : '暂无'
}

function parseQuote(quote: IdiomQuote | null): string {
  if (!quote) {
    return '暂无'
  }
  let text = quote.text ?? ''
  if (quote.book) {
    text += text.length > 0 ? ` ——${quote.book}` : quote.book
  }

  return text.length > 0 ? text : '暂无'
}

function parseExample(example: IdiomExample | null, word: string): string {
  if (!example) {
    return '暂无'
  }
  let text = example.text ?? ''
  if (text.length > 0 && word.length > 0) {
    text = text.split('～').join(word)
  }
  if (example.book) {
    text += text.length > 0 ? ` ——${example.book}` : example.book
  }

  return text.length > 0 ? text : '暂无'
}
