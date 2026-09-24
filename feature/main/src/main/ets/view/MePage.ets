import {
  ColumnStart,
  P100,
  RowSpaceBetweenCenter,
  RowStartCenter,
  SpaceHorizontalLarge,
  SpaceHorizontalSmall,
  SpaceHorizontalXSmall,
  SpaceVerticalMedium,
  SpaceVerticalSmall,
  SpaceVerticalXSmall
} from "designsystem";
import { Footprint } from "model";
import {
  AppNavDestination,
  ArrowRightIcon,
  Avatar,
  Card,
  CardTitleCell,
  CommonIcon,
  IBestBadge,
  IBestCell,
  IBestCellGroup,
  NetWorkImage
} from "ui";
import { MeMenuItem } from "../model/MeMenuItem";
import { OrderStatusItem } from "../model/OrderStatusItem";
import MeViewModel from "../viewmodel/MeViewModel";

/**
 * @file 我的页面视图
 * @author Joker.X
 */
@ComponentV2
export struct MePage {
  /**
   * 我的页面 ViewModel
   */
  @Local
  private vm: MeViewModel = new MeViewModel();

  /**
   * 构建我的页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.me"),
      viewModel: this.vm,
      hideTitleBar: true
    }) {
      this.MeContent();
    }
  }

  /**
   * 我的页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private MeContent(): void {
    List({ space: 12 }) {
      ListItem() {
        this.buildUserInfoSection();
      }

      ListItem() {
        this.buildMembershipCard();
      }

      ListItem() {
        this.buildOrderSection();
      }

      if (this.vm.recentFootprints.length > 0) {
        ListItem() {
          this.buildFootprintSection();
        }
      }

      ListItem() {
        this.buildMenuSection();
      }

      ListItem() {
        SpaceVerticalMedium();
      }
    }
    .padding({
      left: $r("app.float.space_horizontal_medium"),
      right: $r("app.float.space_horizontal_medium"),
      top: $r("app.float.space_vertical_medium"),
      bottom: $r("app.float.space_vertical_medium")
    });
  }

  /**
   * 构建用户信息区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildUserInfoSection(): void {
    RowSpaceBetweenCenter({
      widthValue: P100,
      paddingValue: {
        top: $r("app.float.space_vertical_medium"),
      },
      onTap: (): void => this.vm.onHeadClick()
    }) {
      RowStartCenter() {
        Avatar({
          src: this.vm.userInfo.avatarUrl,
          avatarSize: 68,
          onTap: (): void => this.vm.onHeadClick()
        });

        SpaceHorizontalLarge();

        this.buildUserInfoTitle();
      }

      ArrowRightIcon({ iconSize: 16 });
    }
  }

  /**
   * 构建用户信息标题区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildUserInfoTitle(): void {
    ColumnStart() {
      Text(this.vm.getDisplayName())
        .fontSize($r("app.float.display_medium"))
        .fontColor($r("app.color.text_primary"))
        .fontWeight(FontWeight.Medium);

      SpaceVerticalXSmall();

      this.buildUserPhoneLine();
    }
  }

  /**
   * 构建用户手机号/登录提示
   * @returns {void} 无返回值
   */
  @Builder
  private buildUserPhoneLine(): void {
    if (this.vm.hasPhone()) {
      RowStartCenter() {
        Text($r("app.string.phone_number"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_tertiary"));

        Text(":")
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_tertiary"));

        SpaceHorizontalXSmall();

        Text(this.vm.userInfo.phone)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_tertiary"));
      }
    } else {
      Text($r("app.string.click_to_login"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_tertiary"));
    }
  }

  /**
   * 构建会员权益卡片
   * @returns {void} 无返回值
   */
  @Builder
  private buildMembershipCard(): void {
    Card({
      bgColor: $r("app.color.bg_vip_card"),
      radiusValue: $r("app.float.radius_medium"),
      paddingValue: {
        left: $r("app.float.space_horizontal_large"),
        right: $r("app.float.space_horizontal_large"),
        top: $r("app.float.space_vertical_medium"),
        bottom: $r("app.float.space_vertical_medium")
      }
    }) {
      RowStartCenter({ widthValue: P100 }) {
        RowStartCenter() {
          CommonIcon({
            icon: $r("app.media.ic_vip_fill"),
            iconSize: 20,
            tintColor: $r("app.color.vip_gold")
          });

          SpaceHorizontalSmall();

          Text($r("app.string.member_benefits"))
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.vip_gold"))
            .fontWeight(FontWeight.Bold);
        }

        Blank().layoutWeight(1);

        Text($r("app.string.activate_now"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.vip_gold"))
          .padding({
            left: $r("app.float.space_horizontal_medium"),
            right: $r("app.float.space_horizontal_medium"),
            top: 6,
            bottom: 6
          })
          .border({ width: 1, color: $r("app.color.vip_gold") })
          .borderRadius($r("app.float.radius_large_extra"));
      }
    }
  }

  /**
   * 构建订单区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildOrderSection(): void {
    Card() {
      CardTitleCell({
        leftIcon: $r("app.media.ic_order_fill"),
        leftIconColor: $r("app.color.main_order_icon"),
        title: $r("app.string.my_orders"),
        value: $r("app.string.view_all"),
        onTap: (): void => this.vm.toOrderListPage()
      });

      this.buildOrderStatusRow();
    }
  }

  /**
   * 构建订单状态行
   * @returns {void} 无返回值
   */
  @Builder
  private buildOrderStatusRow(): void {
    Row() {
      ForEach(this.vm.getOrderStatusItems(), (item: OrderStatusItem): void => {
        this.buildOrderStatusItem(item);
      }, (item: OrderStatusItem, index: number): string => `${index}`);
    }
    .width(P100)
    .alignItems(VerticalAlign.Center);
  }

  /**
   * 构建订单状态项
   * @param {OrderStatusItem} item - 订单状态数据
   * @returns {void} 无返回值
   */
  @Builder
  private buildOrderStatusItem(item: OrderStatusItem): void {
    Column() {
      if (item.count > 0) {
        IBestBadge({
          content: this.vm.formatBadgeCount(item.count),
          color: $r("app.color.danger"),
          badgePosition: "top-right"
        }) {
          CommonIcon({
            icon: item.icon,
            iconSize: 24,
            tintColor: $r("app.color.text_primary")
          });
        }
      } else {
        CommonIcon({
          icon: item.icon,
          iconSize: 24,
          tintColor: $r("app.color.text_primary")
        });
      }

      SpaceVerticalXSmall();

      Text(item.label)
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_secondary"));
    }
    .alignItems(HorizontalAlign.Center)
    .layoutWeight(1)
    .padding({
      top: $r("app.float.space_vertical_medium"),
      bottom: $r("app.float.space_vertical_medium")
    })
    .onClick((): void => this.vm.toOrderListByTab(item.tabIndex));
  }

  /**
   * 构建足迹区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildFootprintSection(): void {
    Card() {
      CardTitleCell({
        leftIcon: $r("app.media.ic_footprint_fill"),
        leftIconColor: $r("app.color.main_footprint_icon"),
        title: $r("app.string.my_footprint"),
        value: $r("app.string.view_all"),
        hasBorder: false,
        onTap: (): void => this.vm.toUserFootprintPage()
      });

      List({ space: 8 }) {
        ForEach(this.vm.recentFootprints, (item: Footprint): void => {
          ListItem() {
            this.buildFootprintItem(item);
          }
        }, (item: Footprint): string => `${item.goodsId}`);
      }
      .listDirection(Axis.Horizontal)
      .width(P100)
      .scrollBar(BarState.Off)
      .padding({
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium"),
        bottom: $r("app.float.space_vertical_medium")
      });
    }
  }

  /**
   * 构建单个足迹项
   * @param {Footprint} footprint - 足迹数据
   * @returns {void} 无返回值
   */
  @Builder
  private buildFootprintItem(footprint: Footprint): void {
    Column() {
      NetWorkImage({
        model: footprint.goodsMainPic,
        sizeValue: 100,
        showBackground: true,
        backgroundColorValue: $r("app.color.bg_content"),
        cornerRadius: $r("app.float.radius_small")
      });
    }
    .onClick((): void => this.vm.toGoodsDetailPage(footprint.goodsId));
  }

  /**
   * 构建功能菜单区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildMenuSection(): void {
    ColumnStart({ widthValue: P100 }) {
      this.buildMenuGroup(this.vm.primaryMenus);

      SpaceVerticalSmall();

      this.buildMenuGroup(this.vm.secondaryMenus);
    }
  }

  /**
   * 构建菜单分组
   * @param {MeMenuItem[]} menus - 菜单列表
   * @returns {void} 无返回值
   */
  @Builder
  private buildMenuGroup(menus: MeMenuItem[]): void {
    IBestCellGroup({
      inset: true,
      radius: $r("app.float.radius_medium"),
      outerMargin: 0
    }) {
      ForEach(menus, (item: MeMenuItem): void => {
        IBestCell({
          leftIcon: item.icon,
          leftIconColor: item.iconColor,
          title: item.title,
          isLink: true,
          hasBorder: item.showDivider,
          leftIconMarginRight: 12,
          cellPadding: $r("app.float.space_padding_large"),
          onCellClick: (): void => item.onClick()
        });
      }, (_: MeMenuItem, index: number): string => `${index}`);
    }
  }
}
