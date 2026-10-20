import { Cart, CartGoodsSpec } from "model";
import { AppNavDestination } from "ui";
import CartViewModel from "../viewmodel/CartViewModel";

@ComponentV2
export struct CartPage {
  @Local private vm: CartViewModel = new CartViewModel();

  build() {
    AppNavDestination({ title: "购物车", viewModel: this.vm }) {
      Column({ space: 16 }) {
        Scroll() {
          Column({ space: 12 }) {
            if (this.vm.isLoading) {
              LoadingProgress().width(36).height(36);
            }
            if (this.vm.error) {
              Text(this.vm.error);
              Button("重试").onClick((): void => { this.vm.load(); });
            } else if (!this.vm.isLoading && this.vm.carts.length === 0) {
              Text("购物车暂无商品").fontSize(18).id("cart_empty");
            } else {
              ForEach(this.vm.carts, (cart: Cart): void => {
                Column({ space: 8 }) {
                  Text(cart.goodsName).fontSize(18).fontWeight(FontWeight.Bold);
                  ForEach(cart.spec, (spec: CartGoodsSpec): void => {
                    Text(`${spec.name} × ${spec.count}`);
                  }, (spec: CartGoodsSpec): string => `${spec.id}`);
                }.width("100%").padding(16).backgroundColor($r("app.color.bg_white")).borderRadius(12);
              }, (cart: Cart): string => `${cart.goodsId}`);
            }
          }.width("100%");
        }.width("100%").layoutWeight(1);
        Button("确认订单").width("100%").height(48).id("cart_confirm_order")
          .enabled(!this.vm.navigationBusy).onClick((): void => this.vm.confirmOrder());
      }.width("100%").height("100%").padding(16);
    }
  }
}
