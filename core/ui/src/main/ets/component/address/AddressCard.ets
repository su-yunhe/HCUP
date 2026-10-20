import { Address } from "model";
import { ArrowRightIcon } from "../icon/ArrowRightIcon";

/** Address body and action slot are siblings, so editing never selects an address. */
@ComponentV2
export struct AddressCard {
  @Param address: Address | null = null;
  @Param onTap: () => void = (): void => {};
  @BuilderParam actionSlot: CustomBuilder;
  @Param showBottomBar: boolean = true;
  @Param addressSelected: boolean = false;
  @Param cardId: string = "";
  @Param fieldIdPrefix: string = "address";
  @Param useAddressId: boolean = true;

  build(): void {
    Row({ space: 12 }) {
      Column({ space: 10 }) {
        if (this.address) {
          Text(`${this.address.province} ${this.address.city} ${this.address.district}`)
            .fontSize(19).fontWeight(FontWeight.Medium).fontColor($r("app.color.text_primary"))
            .id(this.fieldId("region", this.address.id));
          Text(this.address.address).fontSize(16).fontColor($r("app.color.text_subtitle"))
            .id(this.fieldId("detail", this.address.id));
          if (this.showBottomBar) {
            Flex({ wrap: FlexWrap.Wrap }) {
              Text(this.address.contact).fontSize(16).fontColor($r("app.color.text_primary"))
                .margin({ right: 12 })
                .id(this.fieldId("contact", this.address.id));
              Text(this.address.phone).fontSize(16).fontColor($r("app.color.text_subtitle"))
                .id(this.fieldId("phone", this.address.id));
            }.width("100%");
            if (this.address.isDefault) {
              Text($r("app.string.address_default")).fontSize(12).fontColor($r("app.color.primary"))
                .padding({ left: 8, right: 8, top: 3, bottom: 3 })
                .border({ width: 1, color: $r("app.color.primary"), radius: 10 })
                .id(this.fieldId("default", this.address.id));
            }
          }
        } else {
          Text($r("app.string.address_not_selected")).fontSize(19).fontColor($r("app.color.text_primary"));
          Text($r("app.string.address_add_hint")).fontSize(16).fontColor($r("app.color.text_subtitle"));
        }
      }.layoutWeight(1).alignItems(HorizontalAlign.Start).padding(16)
        .id(this.cardId || (this.address ? `address_row_${this.address.id}` : "address_empty_card"))
        .onClick((): void => this.onTap());
      if (this.actionSlot) {
        this.actionSlot();
      } else if (this.addressSelected) {
        ArrowRightIcon();
      }
    }.width("100%").padding({ right: 16 }).backgroundColor($r("app.color.bg_white"))
      .borderRadius($r("app.float.radius_medium"));
  }

  private fieldId(field: string, addressId: number): string {
    return `${this.fieldIdPrefix}_${field}${this.useAddressId ? `_${addressId}` : ""}`;
  }
}
