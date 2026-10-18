import { ThemeConst } from 'constants';
import { readBookmarkedSentences, Sentence } from '../model/Sentence';
import { pushPathFrom } from '../utils/NavUtil';

const PAGE_NAME: string = 'SentenceBookmarksPage';

@Builder
export function SentenceBookmarksPageBuilder() {
  SentenceBookmarksPage();
}

/**
 * 诗文名句收藏列表，最新收藏在前
 */
@ComponentV2
export struct SentenceBookmarksPage {
  @Consumer('NavPathStack') pageStack: NavPathStack = new NavPathStack();
  @Local list: Sentence[] = [];
  @Local loaded: boolean = false;

  load() {
    readBookmarkedSentences().then((list: Sentence[]) => {
      this.list = list
      this.loaded = true
    })
  }

  build() {
    NavDestination() {
      Column() {
        if (this.list.length > 0) {
          List() {
            ForEach(this.list, (item: Sentence) => {
              ListItem() {
                Column({ space: 8 }) {
                  Text(item.content)
                    .width('100%')
                    .lineHeight(24)
                  Text(item.from)
                    .width('100%')
                    .fontSize(ThemeConst.FontSize_14)
                    .fontColor(ThemeConst.FontColor_BlockTitle)
                }
                .width('100%')
                .padding(ThemeConst.P_16)
              }
              .id(`sentence_bookmarks_item_${item.id}`)
              .onClick(() => {
                pushPathFrom(this.pageStack, PAGE_NAME, 'SentenceDetailPage', item.id)
              })
            }, (item: Sentence) => item.id.toString())
          }
          .id('sentence_bookmarks_list')
          .width('100%')
          .height('100%')
          .divider({ strokeWidth: 1, color: ThemeConst.CardBackGroundColor_Normal })
        } else if (this.loaded) {
          Text('暂无收藏')
            .id('sentence_bookmarks_empty')
            .width('100%')
            .textAlign(TextAlign.Center)
            .padding(ThemeConst.P_16)
        }
      }
      .id('sentence_bookmarks_page')
      .width('100%')
      .height('100%')
    }
    .title('收藏')
    .onReady((ctx: NavDestinationContext) => {
      this.pageStack = ctx.pathStack
    })
    .onShown(() => {
      // 每次可见都重新查询，反映详情页中的取消收藏
      this.load()
    })
  }
}
