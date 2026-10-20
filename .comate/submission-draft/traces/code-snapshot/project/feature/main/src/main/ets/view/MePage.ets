import { AppNavDestination } from 'ui';
import MeViewModel from '../viewmodel/MeViewModel';

@ComponentV2
export struct MePage {
  @Local private vm: MeViewModel = new MeViewModel();
  @Param embedded: boolean = false;

  @Builder
  private MeContent() {
    Column({ space: 24 }) {
      Text('我的').fontSize(26).fontWeight(FontWeight.Bold).fontColor('#222222').width('100%')
      Row({ space: 16 }) {
        Text('青').fontSize(28).fontColor('#506C5B').width(64).height(64).textAlign(TextAlign.Center)
          .backgroundColor('#E2EAE4').borderRadius(32)
        Column({ space: 8 }) {
          Text('欢迎来到青商城').fontSize(20).fontWeight(FontWeight.Medium).fontColor('#333333')
          Text('当前未登录').fontSize(13).fontColor('#8B8B8B')
        }.alignItems(HorizontalAlign.Start)
      }.width('100%').padding(20).backgroundColor('#FFFFFF').borderRadius(18)
      Column({ space: 22 }) {
        Text('我的收藏').fontSize(16).fontColor('#444444').width('100%')
        Divider().color('#F1F1F1')
        Text('浏览记录').fontSize(16).fontColor('#444444').width('100%')
        Divider().color('#F1F1F1')
        Text('更多生活灵感，等你发现').fontSize(13).fontColor('#999999').width('100%')
      }.width('100%').padding(22).backgroundColor('#FFFFFF').borderRadius(18)
    }.id('me_page').width('100%').height('100%').padding(22)
    .alignItems(HorizontalAlign.Start).backgroundColor('#F6F7F8')
  }

  build() {
    if (this.embedded) { this.MeContent(); } else {
      AppNavDestination({ title: '我的', viewModel: this.vm }) { this.MeContent(); }
    }
  }
}
