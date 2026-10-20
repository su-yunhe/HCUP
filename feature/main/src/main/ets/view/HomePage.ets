import { AppNavDestination } from 'ui';
import HomeViewModel, { HomeProduct } from '../viewmodel/HomeViewModel';

@ComponentV2
export struct HomePage {
  @Local private vm: HomeViewModel = new HomeViewModel();
  @Param embedded: boolean = false;
  @Param scroller: Scroller = new Scroller();
  @Local private yOffset: number = 0;

  @Builder
  private ProductCard(product: HomeProduct) {
    Row({ space: 16 }) {
      Image($rawfile(`products/${product.picture}.svg`))
        .width(96).height(96).objectFit(ImageFit.Contain)
        .backgroundColor('#F1F3F3').borderRadius(14)
      Column({ space: 9 }) {
        Text(product.name).fontSize(17).fontWeight(FontWeight.Medium).fontColor('#222222')
        Text(product.detail).fontSize(12).fontColor('#858585')
        Text(`¥ ${product.price}`).fontSize(18).fontWeight(FontWeight.Bold).fontColor('#252525')
      }.alignItems(HorizontalAlign.Start).layoutWeight(1)
    }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(18)
  }

  @Builder
  private HomeContent() {
    Column() {
      Scroll(this.scroller) {
        Column({ space: 18 }) {
          Row() {
            Column({ space: 5 }) {
              Text('青商城').fontSize(25).fontWeight(FontWeight.Bold).fontColor('#202725')
              Text('好物相伴，悦享日常').fontSize(12).fontColor('#7C8581')
            }.alignItems(HorizontalAlign.Start)
            Blank()
            Text('生活好物').fontSize(12).fontColor('#53645D')
              .padding({ left: 12, right: 12, top: 7, bottom: 7 })
              .backgroundColor('#E8EDE9').borderRadius(20)
          }.width('100%').padding({ top: 12, bottom: 3 })
          Row() {
            Column({ space: 7 }) {
              Text('新人专享优惠券').fontSize(17).fontWeight(FontWeight.Bold).fontColor('#403725')
              Text('发现心仪好物，开启品质生活').fontSize(12).fontColor('#8B795E')
            }.alignItems(HorizontalAlign.Start).layoutWeight(1)
            Text('领取').id('home_coupon_receive').fontSize(14).fontWeight(FontWeight.Medium)
              .fontColor('#FFFFFF').padding({ left: 19, right: 19, top: 10, bottom: 10 })
              .backgroundColor('#3A4039').borderRadius(22)
          }.width('100%').padding(20).height(106).backgroundColor('#F3E8D1').borderRadius(18)
          Row() {
            Column({ space: 12 }) {
              Text('把日常过成喜欢的样子').fontSize(21).fontWeight(FontWeight.Bold).fontColor('#284839')
              Text('从一杯热茶，到一盏柔光\n甄选实用与美感兼具的生活好物').fontSize(12)
                .lineHeight(21).fontColor('#647C70')
              Text('本地好物精选').fontSize(11).fontColor('#426653')
            }.alignItems(HorizontalAlign.Start).layoutWeight(1)
            Image($rawfile('products/vase.svg')).width(105).height(140)
          }.width('100%').padding(18).backgroundColor('#E4EDE7').borderRadius(20)
          Column({ space: 12 }) {
            Row() {
              Text('限时精选').fontSize(20).fontWeight(FontWeight.Bold).fontColor('#222222')
              Blank()
              Text('精选日常好物').fontSize(12).fontColor('#919191')
            }.width('100%')
            Row({ space: 12 }) {
              Column({ space: 7 }) {
                Image($rawfile('products/mug.svg')).width('100%').height(112).objectFit(ImageFit.Contain)
                Text('温暖一杯').fontSize(14).fontColor('#333333')
                Text('陶瓷马克杯 · ¥39').fontSize(12).fontColor('#777777')
              }.layoutWeight(1).padding(14).backgroundColor('#FFFFFF').borderRadius(18)
              Column({ space: 7 }) {
                Image($rawfile('products/lamp.svg')).width('100%').height(112).objectFit(ImageFit.Contain)
                Text('点亮角落').fontSize(14).fontColor('#333333')
                Text('柔光阅读灯 · ¥129').fontSize(12).fontColor('#777777')
              }.layoutWeight(1).padding(14).backgroundColor('#FFFFFF').borderRadius(18)
            }.width('100%')
          }.id('home_flash_sale').width('100%')
          Column({ space: 12 }) {
            Row() {
              Text('推荐商品').fontSize(20).fontWeight(FontWeight.Bold).fontColor('#222222')
              Blank()
              Text('为生活增添小美好').fontSize(12).fontColor('#919191')
            }.width('100%')
            ForEach(this.vm.products, (product: HomeProduct) => {
              this.ProductCard(product);
            }, (product: HomeProduct): string => product.id)
          }.id('home_recommend').width('100%')
          Text('用心挑选，陪伴每一天').fontSize(12).fontColor('#A0A5A1').padding({ top: 10, bottom: 22 })
        }.width('100%').padding({ left: 18, right: 18, bottom: 10 })
      }
      .id('home_scroll').width('100%').height('100%')
      .scrollable(ScrollDirection.Vertical).scrollBar(BarState.Off)
      .accessibilityDescription(`{"yOffset":${this.yOffset}}`)
      .onDidScroll(() => { this.yOffset = this.scroller.currentOffset().yOffset; })
    }.id('home_page').width('100%').height('100%').backgroundColor('#F6F7F8')
  }

  build() {
    if (this.embedded) { this.HomeContent(); } else {
      AppNavDestination({ title: '首页', viewModel: this.vm }) { this.HomeContent(); }
    }
  }
}
