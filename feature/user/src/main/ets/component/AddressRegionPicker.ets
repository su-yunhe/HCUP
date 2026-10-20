import { CascaderOption } from "../model/AddressRegionData";
import { addressRegions, RegionSelection, resolveRegion } from "../model/AddressRegion";

@ComponentV2
export struct AddressRegionPicker {
  @Param selection: RegionSelection = new RegionSelection();
  @Param onConfirm: (value: RegionSelection) => void = (): void => {};
  @Param onCancel: () => void = (): void => {};
  @Local private provinceCode: string = "";
  @Local private cityCode: string = "";
  @Local private districtCode: string = "";
  @Local private provinces: CascaderOption[] = addressRegions;

  aboutToAppear(): void {
    this.provinceCode = this.selection.provinceCode;
    this.cityCode = this.selection.cityCode;
    this.districtCode = this.selection.districtCode;
  }

  private cities(): CascaderOption[] {
    return this.provinces.find((item: CascaderOption): boolean => item.value === this.provinceCode)?.children ?? [];
  }

  private districts(): CascaderOption[] {
    return this.cities().find((item: CascaderOption): boolean => item.value === this.cityCode)?.children ?? [];
  }

  private chooseProvince(item: CascaderOption): void {
    if (this.provinceCode !== item.value) {
      this.provinceCode = item.value;
      this.cityCode = "";
      this.districtCode = "";
    }
  }

  private chooseCity(item: CascaderOption): void {
    if (this.cityCode !== item.value) {
      this.cityCode = item.value;
      this.districtCode = "";
    }
  }

  build() {
    Stack({ alignContent: Alignment.Bottom }) {
      Column().width("100%").height("100%").backgroundColor("#66000000").onClick((): void => this.onCancel());
      Column({ space: 12 }) {
        Text("选择所在地区").fontSize(20).fontWeight(FontWeight.Bold);
        Row() {
          Text("省").layoutWeight(1).textAlign(TextAlign.Center);
          Text("市").layoutWeight(1).textAlign(TextAlign.Center);
          Text("区").layoutWeight(1).textAlign(TextAlign.Center);
        }.width("100%");
        if (this.provinces.length > 0) {
          Row({ space: 4 }) {
            List() {
              ForEach(this.provinces, (item: CascaderOption): void => {
                ListItem() {
                  Text(item.text).width("100%").padding(12).fontSize(15)
                    .fontColor(this.provinceCode === item.value ? $r("app.color.primary") : $r("app.color.text_primary"))
                    .backgroundColor(this.provinceCode === item.value ? $r("app.color.bg_grey") : $r("app.color.bg_white"))
                    .id(`region_province_${item.value}`).onClick((): void => this.chooseProvince(item));
                }
              }, (item: CascaderOption): string => item.value);
            }.layoutWeight(1).height("100%").id("address_region_province_list");
            List() {
              ForEach(this.cities(), (item: CascaderOption): void => {
                ListItem() {
                  Text(item.text).width("100%").padding(12).fontSize(15)
                    .fontColor(this.cityCode === item.value ? $r("app.color.primary") : $r("app.color.text_primary"))
                    .backgroundColor(this.cityCode === item.value ? $r("app.color.bg_grey") : $r("app.color.bg_white"))
                    .id(`region_city_${item.value}`).onClick((): void => this.chooseCity(item));
                }
              }, (item: CascaderOption): string => item.value);
            }.layoutWeight(1).height("100%").id("address_region_city_list");
            List() {
              ForEach(this.districts(), (item: CascaderOption): void => {
                ListItem() {
                  Text(item.text).width("100%").padding(12).fontSize(15)
                    .fontColor(this.districtCode === item.value ? $r("app.color.primary") : $r("app.color.text_primary"))
                    .backgroundColor(this.districtCode === item.value ? $r("app.color.bg_grey") : $r("app.color.bg_white"))
                    .id(`region_district_${item.value}`).onClick((): void => { this.districtCode = item.value; });
                }
              }, (item: CascaderOption): string => item.value);
            }.layoutWeight(1).height("100%").id("address_region_district_list");
          }.width("100%").layoutWeight(1);
        } else {
          Text("地区数据加载失败").layoutWeight(1);
          Button("重试").onClick((): void => { this.provinces = addressRegions; });
        }
        Row({ space: 20 }) {
          Button("取消").id("region_cancel").layoutWeight(1).onClick((): void => this.onCancel());
          Button("确认").id("region_confirm").layoutWeight(1)
            .enabled(resolveRegion(this.provinceCode, this.cityCode, this.districtCode) !== null)
            .onClick((): void => {
              const result: RegionSelection | null = resolveRegion(this.provinceCode, this.cityCode, this.districtCode);
              if (result) {
                this.onConfirm(result);
              }
            });
        }.width("100%");
      }.width("100%").height("75%").padding(16).backgroundColor($r("app.color.bg_white"))
        .borderRadius({ topLeft: 16, topRight: 16 }).id("address_region_picker");
    }.width("100%").height("100%");
  }
}
