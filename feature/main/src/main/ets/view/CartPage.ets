import { AppNavDestination, EmptyCart } from 'ui';
import CartViewModel from '../viewmodel/CartViewModel';

@ComponentV2
export struct CartPage {
  @Local private vm: CartViewModel = new CartViewModel();
  @Param embedded: boolean = false;

  @Builder
  private CartContent() {
    Column() {
      Text('购物车').fontSize(26).fontWeight(FontWeight.Bold).fontColor('#222222')
        .width('100%').padding(22)
      Column() {
        EmptyCart()
        Text('去首页发现喜欢的好物吧').fontSize(14).fontColor('#999999').margin({ top: 12 })
      }.layoutWeight(1).width('100%').justifyContent(FlexAlign.Center)
    }.id('cart_page').width('100%').height('100%').backgroundColor('#F6F7F8')
  }

  build() {
    if (this.embedded) { this.CartContent(); } else {
      AppNavDestination({ title: '购物车', viewModel: this.vm }) { this.CartContent(); }
    }
  }
}
