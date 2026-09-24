import {
  ColumnStart,
  P100,
  RowStartCenter,
  SpaceHorizontalSmall,
  SpaceHorizontalXSmall,
  SpaceVerticalMedium,
  SpaceVerticalSmall,
  SpaceVerticalXSmall
} from "designsystem";
import { Logistics, LogisticsItem, Order } from "model";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { AddressCard, AppNavDestination, BaseNetWorkView, Card, NetWorkImage, TitleWithLine } from "ui";
import { IBestCell, IBestCellGroup, IBestStep, IBestSteps } from "ibestui";
import OrderLogisticsViewModel from "../viewmodel/OrderLogisticsViewModel";

/**
 * @file 订单物流页面视图
 * @author Joker.X
 */
@ComponentV2
export struct OrderLogisticsPage {
  /**
   * 订单物流页面 ViewModel
   */
  @Local
  private vm: OrderLogisticsViewModel = new OrderLogisticsViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();
  /**
   * 物流步骤条分组 ID
   */
  @Local
  private stepsGroupId: string = "order_logistics_steps";

  /**
   * 构建订单物流页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.order_logistics"),
      viewModel: this.vm,
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      }
    }) {
      this.PageContent();
    }
  }

  /**
   * 页面内容
   * @returns {void} 无返回值
   */
  @Builder
  private PageContent(): void {
    BaseNetWorkView({
      uiState: this.vm.uiState,
      onRetry: (): void => this.vm.retryRequest(),
      content: (): void => this.OrderLogisticsContent()
    });
  }

  /**
   * 订单物流页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private OrderLogisticsContent(): void {
    ColumnStart({ fillMaxSize: true }) {
      Scroll() {
        Column() {
          AddressCard({
            address: this.getOrderData().address ?? null
          });

          SpaceVerticalMedium();

          this.LogisticsInfoCard(this.getLogisticsData());

          SpaceVerticalMedium();

          this.LogisticsTrackCard(this.getLogisticsData());

          SpaceVerticalMedium();
        }
        .padding({
          left: $r("app.float.space_horizontal_medium"),
          right: $r("app.float.space_horizontal_medium"),
          top: $r("app.float.space_vertical_medium"),
          bottom: $r("app.float.space_vertical_medium")
        });
      }
      .layoutWeight(1)
      .scrollBar(BarState.Off);
    }
  }

  /**
   * 物流信息卡片
   * @param {Logistics} logistics - 物流信息
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsInfoCard(logistics: Logistics): void {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          hasBorder: true,
          titleBuilder: (): void => this.LogisticsInfoTitle(),
          rightIconBuilder: (): void => this.LogisticsLogo(logistics)
        });

        IBestCell({
          title: $r("app.string.express_company"),
          hasBorder: true,
          value: logistics.expName ?? $r("app.string.unknown_express")
        });

        IBestCell({
          title: $r("app.string.logistics_number"),
          hasBorder: true,
          valueBuilder: (): void => this.LogisticsNumberValue(logistics)
        });

        IBestCell({
          title: $r("app.string.courier"),
          hasBorder: true,
          value: logistics.courier ?? $r("app.string.none")
        });

        IBestCell({
          title: $r("app.string.contact_phone"),
          hasBorder: true,
          valueBuilder: (): void => this.LogisticsPhoneValue(logistics)
        });

        IBestCell({
          title: $r("app.string.transport_time"),
          hasBorder: false,
          value: logistics.takeTime ?? $r("app.string.none")
        });
      }
    }
  }

  /**
   * 物流信息标题
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsInfoTitle(): void {
    TitleWithLine({
      text: $r("app.string.logistics_info")
    });
  }

  /**
   * 物流公司图标
   * @param {Logistics} logistics - 物流信息
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsLogo(logistics: Logistics): void {
    NetWorkImage({
      model: logistics.logo ?? "",
      sizeValue: 18
    });
  }

  /**
   * 物流编号展示区域
   * @param {Logistics} logistics - 物流信息
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsNumberValue(logistics: Logistics): void {
    RowStartCenter() {
      Text(logistics.number ?? $r("app.string.none"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_secondary"));

      SpaceHorizontalSmall();

      Text($r("app.string.copy"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.primary"));

      SpaceHorizontalXSmall();
    }
  }

  /**
   * 物流联系电话展示区域
   * @param {Logistics} logistics - 物流信息
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsPhoneValue(logistics: Logistics): void {
    RowStartCenter() {
      Text(logistics.courierPhone ?? $r("app.string.none"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_secondary"));

      SpaceHorizontalSmall();

      Text($r("app.string.call"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.primary"));

      SpaceHorizontalXSmall();
    }
  }

  /**
   * 物流轨迹卡片
   * @param {Logistics} logistics - 物流信息
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsTrackCard(logistics: Logistics): void {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          hasBorder: true,
          titleBuilder: (): void => this.LogisticsTrackTitle()
        });
      }

      this.LogisticsStepsContent(logistics.list ?? []);
    }
  }

  /**
   * 物流轨迹标题
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsTrackTitle(): void {
    TitleWithLine({
      text: $r("app.string.logistics_track")
    });
  }

  /**
   * 物流步骤条内容
   * @param {LogisticsItem[]} logisticsItems - 物流轨迹列表
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsStepsContent(logisticsItems: LogisticsItem[]): void {
    if (logisticsItems.length > 0) {
      ColumnStart({ widthValue: P100, paddingValue: $r("app.float.space_padding_medium") }) {
        IBestSteps({
          groupId: this.stepsGroupId,
          active: 0,
          dotSize: 8,
          placeDirection: Axis.Vertical,
          inactiveColor: $r("app.color.border"),
          activeColor: $r("app.color.primary")
        }) {
          ForEach(logisticsItems, (item: LogisticsItem, index: number): void => {
            IBestStep({
              groupId: this.stepsGroupId,
              type: "dot"
            }) {
              this.LogisticsStepItem(item, index);
            }
          }, (item: LogisticsItem, index: number): string => `${index}-${item.time ?? ""}`);
        }
      }
    }
  }

  /**
   * 物流步骤条项
   * @param {LogisticsItem} item - 物流轨迹项
   * @param {number} index - 当前索引
   * @returns {void} 无返回值
   */
  @Builder
  private LogisticsStepItem(item: LogisticsItem, index: number): void {
    ColumnStart({
      paddingValue: { right: $r("app.float.space_horizontal_medium") }
    }) {
      if (item.status) {
        Text(item.status)
          .fontSize($r("app.float.body_large"))
          .fontColor(this.getStepStatusColor(index));
      }

      if (item.time) {
        SpaceVerticalSmall();
        Text(item.time)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_tertiary"));
      }
    }
  }

  /**
   * 获取步骤条状态颜色
   * @param {number} index - 当前索引
   * @returns {ResourceColor} 状态颜色
   */
  private getStepStatusColor(index: number): ResourceColor {
    return index === 0 ? $r("app.color.text_primary") : $r("app.color.text_secondary");
  }

  /**
   * 获取订单数据
   * @returns {Order} 订单数据
   */
  private getOrderData(): Order {
    return this.vm.data ?? new Order();
  }

  /**
   * 获取物流数据
   * @returns {Logistics} 物流数据
   */
  private getLogisticsData(): Logistics {
    return this.vm.logisticsInfo ?? new Logistics();
  }
}
