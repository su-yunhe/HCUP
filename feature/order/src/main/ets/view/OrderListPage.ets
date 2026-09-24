import { P100 } from "designsystem";
import { Order } from "model";
import { OrderNavigator } from "navigation";
import { AppNavDestination, BaseNetWorkListView, OrderGoodsModal, RefreshLayout } from "ui";
import { OrderCard } from "../component/OrderCard";
import OrderListViewModel from "../viewmodel/OrderListViewModel";

/**
 * @file 订单列表页面视图
 * @author Joker.X
 */
@ComponentV2
export struct OrderListPage {
  /**
   * 订单列表页面 ViewModel
   */
  @Local
  private vm: OrderListViewModel = new OrderListViewModel();
  /**
   * 列表滚动控制器
   */
  private listScroller: Scroller = new Scroller();

  /**
   * 构建订单列表页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.order_list"),
      viewModel: this.vm
    }) {
      BaseNetWorkListView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.OrderListContent()
      });
      OrderGoodsModal({
        visible: this.vm.rebuyModalVisible,
        title: $r("app.string.select_goods_to_buy"),
        buttonText: $r("app.string.rebuy"),
        cartList: this.vm.rebuyCartList,
        onDismiss: (): void => this.vm.hideRebuyModal(),
        onItemButtonClick: (goodsId: number): void => this.vm.toGoodsDetailForRebuy(goodsId)
      });

      OrderGoodsModal({
        visible: this.vm.commentModalVisible,
        title: $r("app.string.select_goods_to_comment"),
        buttonText: $r("app.string.go_to_comment"),
        cartList: this.vm.commentCartList,
        onDismiss: (): void => this.vm.hideCommentModal(),
        onItemButtonClick: (goodsId: number): void => this.vm.toOrderCommentForGoods(goodsId)
      });
    }
  }

  /**
   * 订单列表页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private OrderListContent() {
    RefreshLayout({
      loading: this.vm.isLoading,
      isEnableSlideUp: this.vm.isEnableSlideUp,
      scroller: this.listScroller,
      onRefresh: (direction): void => this.vm.onRefreshDirection(direction)
    }) {
      List({ space: 12, scroller: this.listScroller }) {
        ForEach(this.vm.listData, (item: Order): void => {
          ListItem() {
            this.OrderListItem(item);
          }
        }, (item: Order): string => `${item.id}`);
      }
      .width(P100)
      .height(P100)
      .padding({
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium")
      })
      .edgeEffect(EdgeEffect.None);
    }
  }

  /**
   * 渲染订单列表项
   * @param {Order} item - 订单数据
   * @returns {void} 无返回值
   */
  @Builder
  private OrderListItem(item: Order): void {
    OrderCard({
      order: item,
      toOrderDetail: (orderId: number): void => OrderNavigator.toDetail(orderId),
      toPay: (): void => this.vm.toPay(item),
      toGoodsDetail: (): void => this.vm.handleRebuy(item),
      toLogistics: (): void => OrderNavigator.toLogistics(item.id),
      toComment: (): void => this.vm.handleOrderComment(item),
      toRefund: (): void => OrderNavigator.toRefund(item.id)
    });
  }
}
