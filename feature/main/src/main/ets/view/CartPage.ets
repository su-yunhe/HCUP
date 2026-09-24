import { ColumnStart, P100, SpaceVerticalMedium } from "designsystem";
import { Cart, CartGoodsSpec } from "model";
import { GoodsNavigator } from "navigation";
import { AppNavDestination, EmptyCart, OrderGoodsCard } from "ui";
import { IBestCheckbox } from "ibestui";
import CartViewModel from "../viewmodel/CartViewModel";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { CartBottomBar } from "../component/CartBottomBar";

/**
 * @file 购物车页面视图
 * @author Joker.X
 */
@ComponentV2
export struct CartPage {
  /**
   * 购物车页面 ViewModel
   */
  @Local
  private vm: CartViewModel = new CartViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();
  /**
   * main 页面当前选中的页面索引
   */
  @Param
  currentPageIndex: number = 0;

  /**
   * 监听 main 页面当前选中的页面索引变化
   */
  @Monitor('currentPageIndex')
  onPageIndexChange() {
    if (this.currentPageIndex === 2) {
      this.vm.loadCartData();
    }
  }

  /**
   * 构建购物车页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.cart"),
      viewModel: this.vm,
      menus: this.vm.isEmpty ? [] : [
        {
          value: "",
          icon: this.vm.isEditing
            ? $r("app.media.ic_success")
            : $r("app.media.ic_edit"),
          action: (): void => {
            this.vm.toggleEditMode();
          }
        }
      ],
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      },
    }) {
      ColumnStart({ fillMaxSize: true }) {
        this.CartContent();
        if (!this.vm.isEmpty) {
          CartBottomBar({
            safeAreaEnabled: false,
            isAllSelected: this.vm.isAllSelected,
            isEditing: this.vm.isEditing,
            selectedCount: this.vm.selectedCount,
            totalAmount: this.vm.totalAmount,
            onToggleSelectAll: (): void => {
              this.vm.toggleSelectAll();
            },
            onDeleteClick: (): void => {
              this.vm.deleteSelected();
            },
            onSettleClick: (): void => {
              this.vm.onSettleClick();
            },
            windowSafeAreaState: this.windowSafeAreaState
          });
        }
      }
    }
  }

  /**
   * 购物车页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private CartContent() {
    if (this.vm.isEmpty) {
      EmptyCart();
    } else {
      List({ space: 12 }) {
        // 空的 ListItem 用于分隔购物车商品和底部栏
        ListItem() {
        }

        ForEach(this.vm.cartList, (cart: Cart) => {
          ListItem() {
            OrderGoodsCard({
              data: cart,
              onGoodsClick: (goodsId: number): void => {
                GoodsNavigator.toDetail(goodsId);
              },
              onQuantityChanged: (specId: number, count: number): void => {
                this.vm.updateSpecCount(cart.goodsId, specId, count);
              },
              enableQuantityStepper: true,
              itemSelectSlotBuilder: (spec: CartGoodsSpec): void => {
                this.CheckboxSlot(cart.goodsId, spec);
              }
            });
          }
        }, (cart: Cart): string => JSON.stringify(cart));
        ListItem() {
        }
      }
      .width(P100)
      .padding({
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium"),
      })
      .layoutWeight(1)

      .scrollBar(BarState.Off);
    }
  }

  /**
   * 选择框插槽
   * @param {number} goodsId 商品ID
   * @param {CartGoodsSpec} spec 规格信息
   * @returns {void} 无返回值
   */
  @Builder
  private CheckboxSlot(goodsId: number, spec: CartGoodsSpec) {
    IBestCheckbox({
      value: this.vm.isSpecSelected(goodsId, spec.id),
      shape: "round",
      onChange: (): void => {
        this.vm.toggleSpecSelected(goodsId, spec.id);
      }
    });
  }
}
