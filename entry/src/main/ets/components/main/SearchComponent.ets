import { promptAction, router } from "@kit.ArkUI"

// 占位文案与空内容提示共用同一文案
const SEARCH_HINT: string = '请输入搜索内容'

@Component
export struct SearchComponent {
  @State searchKeyword:string = ''

  build() {
    Column() {
      // 搜索框和按钮
      Row({ space: 10 }) {
        // 搜索框
        TextInput({ placeholder: SEARCH_HINT }).width('70%').backgroundColor('#ffdbd9d9').height(40)
          .placeholderColor('#FF808080')
          .fontColor('#FF121212')
          .id('search_input')
          .onChange((value:string) => {
            this.searchKeyword = value
          })

        //搜索按钮
        Button() {
          Image($r('app.media.ic_public_search_filled')).fillColor(Color.White).width(30)
        }
        .type(ButtonType.Circle)
        .width(40)
        .height(40)
        .id('search_button')
        .onClick(() => {
          if(this.searchKeyword.trim()) {
            router.pushUrl({
              url: 'pages/SongsListPage',
              params: { 'searchKeyword': this.searchKeyword }
            })
          } else { promptAction.showToast({ message: SEARCH_HINT }) }
        })
      }.width('100%').justifyContent(FlexAlign.Center)
    }
    .backgroundColor(Color.Transparent)
  }
}