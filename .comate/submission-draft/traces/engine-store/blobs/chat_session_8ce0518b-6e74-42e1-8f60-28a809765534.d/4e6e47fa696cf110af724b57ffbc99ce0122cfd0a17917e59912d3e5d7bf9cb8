import { ClassicPoem, readClassicPoem } from '../model/ClassicPoem';
import { ClassicPoemView } from '../view/ClassicPoemView';

@Builder
export function ClassicPoemDetailPageBuilder() {
  ClassicPoemDetailPage();
}

/**
 * 按 id 展示一首诗词，路由参数为诗词 id（number）
 */
@ComponentV2
export struct ClassicPoemDetailPage {
  @Consumer('NavPathStack') pageStack: NavPathStack = new NavPathStack();
  @Local classicPoem: ClassicPoem | null = null;
  @Local loaded: boolean = false;

  build() {
    NavDestination() {
      Column() {
        if (this.classicPoem) {
          Scroll() {
            ClassicPoemView({
              classicPoem: this.classicPoem
            })
          }
          .align(Alignment.Top)
          .height('100%')
        } else if (this.loaded) {
          Text('暂无数据')
            .width('100%')
            .textAlign(TextAlign.Center)
            .padding(16)
        }
      }
      // 页面 id 不设在 NavDestination 上，否则系统标题栏/返回按钮的 key 会被追加该 id
      .id('poem_detail_page')
      .width('100%')
      .height('100%')
    }
    .title(this.classicPoem ? this.classicPoem.title : '')
    .onReady((ctx: NavDestinationContext) => {
      this.pageStack = ctx.pathStack
      const poemId = ctx.pathInfo.param as number
      readClassicPoem(poemId).then((value: ClassicPoem | null) => {
        this.classicPoem = value
        this.loaded = true
      })
    })
  }
}
