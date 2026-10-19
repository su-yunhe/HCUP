import { promptAction, router } from "@kit.ArkUI"
import { ToastUtil } from "@pura/harmony-utils"
import { PlayController } from "../play/PlayController"

@Component
export struct SearchComponent {
  @State searchKeyword:string = ''

  // 提交搜索（搜索按钮与回车共用），纯空格按空输入处理
  private submitSearch: () => void = () => {
    if(this.searchKeyword.trim()) {
      router.pushUrl({
        url: 'pages/SongsListPage',
        params: { 'searchKeyword': this.searchKeyword }
      })
    } else { ToastUtil.showToast('请输入搜索内容') }
  }

  build() {
    Column() {
      // 搜索框和按钮
      Row({ space: 10 }) {
        // 搜索框
        TextInput({ placeholder: '请输入搜索内容' }).layoutWeight(1).backgroundColor('#ffdbd9d9').height(40).placeholderColor(Color.Gray).fontColor(Color.Black)
          .id('search_input')
          .onChange((value:string) => {
            this.searchKeyword = value
          })
          .onSubmit(() => {
            this.submitSearch()
          })

        //搜索按钮
        Button({type:ButtonType.Circle}) {
          Image($r('app.media.ic_public_search_filled')).width(20).fillColor(Color.White).margin(10)
        }
        .id('search_button')
        .backgroundColor('#ff3587c8')
        .width(40)
        .height(40)
        .onClick(() => {
          this.submitSearch()
        })

        PlayController()

      }
      .borderRadius(20)
      .justifyContent(FlexAlign.Center)
      .padding({ left:30, right:30})
    }
    .backgroundColor(Color.Transparent)
  }
}
