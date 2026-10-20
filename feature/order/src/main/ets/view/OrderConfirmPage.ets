import { Cart, CartGoodsSpec } from "model";
import { AddressCard, AppNavDestination } from "ui";
import OrderConfirmViewModel from "../viewmodel/OrderConfirmViewModel";

@ComponentV2
export struct OrderConfirmPage {
  @Local private vm: OrderConfirmViewModel = new OrderConfirmViewModel();

  build() {
    AppNavDestination({ title: "确认订单", viewModel: this.vm }) {
      Scroll() {
        Column({ space: 16 }) {
          Text("收货地址").fontSize(20).fontWeight(FontWeight.Bold);
          if (this.vm.addressLoading) {
            LoadingProgress().width(32).height(32).id("order_address_loading");
          }
          if (this.vm.addressError) {
            Text(this.vm.addressError).id("order_address_error");
            Button("重试同步").id("order_address_retry").enabled(!this.vm.addressLoading)
              .onClick((): void => { this.vm.revalidate(); });
          }
          Column() {
            AddressCard({
              address: this.vm.selectedAddress, cardId: "order_address_card", fieldIdPrefix: "order_address",
              useAddressId: false, addressSelected: true,
              onTap: (): void => this.vm.selectAddress()
            });
          }.width("100%").id("order_address_entry").onClick((): void => this.vm.selectAddress());
          Text("商品信息").fontSize(20).fontWeight(FontWeight.Bold);
          if (this.vm.cartError) {
            Text(this.vm.cartError);
            Button("重试").onClick((): void => { this.vm.loadCarts(); });
          } else if (this.vm.carts.length === 0) {
            Text("购物车暂无商品").fontColor($r("app.color.text_subtitle"));
          } else {
            ForEach(this.vm.carts, (cart: Cart): void => {
              Column({ space: 8 }) {
                Text(cart.goodsName).fontSize(18);
                ForEach(cart.spec, (spec: CartGoodsSpec): void => {
                  Text(`${spec.name} × ${spec.count}`);
                }, (spec: CartGoodsSpec): string => `${spec.id}`);
              }.width("100%").padding(16).backgroundColor($r("app.color.bg_white")).borderRadius(12);
            }, (cart: Cart): string => `${cart.goodsId}`);
          }
        }.width("100%").padding(16).alignItems(HorizontalAlign.Start).id("order_confirm_page");
      }.width("100%").height("100%");
    }
  }
}
