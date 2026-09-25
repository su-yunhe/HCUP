import { IBestTag } from "ibestui";
import {
  P100,
  RowSpaceBetweenCenter,
  RowStartCenter,
  SpaceHorizontalLarge,
  SpaceVerticalXSmall,
  columnStart
} from "designsystem";
import { Address } from "model";
import { ArrowRightIcon } from "../icon/ArrowRightIcon";
import { Card } from "../card/Card";

/**
 * @file 通用收货地址卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct AddressCard {
  /**
   * 地址数据，为 null 时显示选择地址布局
   */
  @Param
  address: Address | null = null;
  /**
   * 卡片点击回调
   */
  @Param
  onTap: () => void = () => {
  };
  /**
   * 右上角操作区域插槽，可根据场景定制
   */
  @BuilderParam
  actionSlot: CustomBuilder;
  /**
   * 是否显示底部栏，包含联系人和标签
   */
  @Param
  showBottomBar: boolean = true;
  /**
   * 在订单确认页标记为已选中的地址
   */
  @Param
  addressSelected: boolean = false;

  /**
   * 构建收货地址卡片
   * @returns {void} 无返回值
   */
  build(): void {
    Card({
      onTap: (): void => this.onTap()
    }) {
      if (this.address) {
        this.buildAddressContent(this.address);
      } else {
        this.buildEmptyContent();
      }
    }
  }

  /**
   * 构建地址内容区域
   * @param {Address} address - 地址数据
   * @returns {void} 无返回值
   */
  @Builder
  private buildAddressContent(address: Address): void {
    this.buildAddressHeader(address);

    if (this.showBottomBar) {
      this.buildDivider();
      this.buildAddressBottomBar(address);
    }
  }

  /**
   * 构建地址头部信息
   * @param {Address} address - 地址数据
   * @returns {void} 无返回值
   */
  @Builder
  private buildAddressHeader(address: Address): void {
    RowSpaceBetweenCenter({
      widthValue: P100,
      paddingValue: $r("app.float.space_padding_medium")
    }) {
      Column() {
        Text(this.buildRegionText(address))
          .fontSize($r("app.float.headline_large"))
          .fontColor($r("app.color.text_primary"))
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis });

        SpaceVerticalXSmall();

        Text(address.address)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_subtitle"))
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis });
      }
      .layoutWeight(1)
      .margin({ right: $r("app.float.space_horizontal_small") })
      .attributeModifier(columnStart());

      if (this.actionSlot) {
        // 自定义操作区域优先
        this.actionSlot();
      } else if (this.addressSelected) {
        // 订单确认页选中时显示箭头
        ArrowRightIcon();
      }
    }
  }

  /**
   * 构建地址底部栏
   * @param {Address} address - 地址数据
   * @returns {void} 无返回值
   */
  @Builder
  private buildAddressBottomBar(address: Address): void {
    RowSpaceBetweenCenter({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_horizontal_large"),
        right: $r("app.float.space_horizontal_large"),
        top: $r("app.float.space_vertical_medium"),
        bottom: $r("app.float.space_vertical_medium")
      }
    }) {
      RowStartCenter() {
        Text(address.contact)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_subtitle"))
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis });

        SpaceHorizontalLarge();

        Text(address.phone)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_subtitle"))
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis });
      }

      if (address.isDefault) {
        IBestTag({
          text: $r("app.string.address_default"),
          type: "primary",
          round: true,
          tagSize: "medium"
        });
      }
    }
  }

  /**
   * 构建空地址状态内容
   * @returns {void} 无返回值
   */
  @Builder
  private buildEmptyContent(): void {
    RowSpaceBetweenCenter({
      widthValue: P100,
      paddingValue: $r("app.float.space_padding_medium")
    }) {
      Text($r("app.string.address_not_selected"))
        .fontSize($r("app.float.headline_large"))
        .fontColor($r("app.color.text_primary"))
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis });

      ArrowRightIcon();
    }

    this.buildDivider();

    RowStartCenter({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_horizontal_large"),
        right: $r("app.float.space_horizontal_large"),
        top: $r("app.float.space_vertical_medium"),
        bottom: $r("app.float.space_vertical_medium")
      }
    }) {
      Text($r("app.string.address_add_hint"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_tertiary"))
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis });
    }
  }

  /**
   * 构建分割线
   * @returns {void} 无返回值
   */
  @Builder
  private buildDivider(): void {
    Column()
      .width(P100)
      .height($r("app.float.space_divider"))
      .backgroundColor($r("app.color.border"));
  }

  /**
   * 拼接省市区文本
   * @param {Address} address - 地址数据
   * @returns {string} 省市区拼接结果
   */
  private buildRegionText(address: Address): string {
    return `${address.province}${address.city}${address.district}`;
  }
}