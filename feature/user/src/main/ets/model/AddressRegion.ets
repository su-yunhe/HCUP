import { CascaderOption, regionData } from "./AddressRegionData";

export class RegionSelection {
  provinceCode: string = "";
  cityCode: string = "";
  districtCode: string = "";
  province: string = "";
  city: string = "";
  district: string = "";
}

export const addressRegions: CascaderOption[] = regionData;

export function resolveRegion(provinceCode: string, cityCode: string, districtCode: string): RegionSelection | null {
  const province: CascaderOption | undefined = addressRegions.find((item: CascaderOption): boolean => item.value === provinceCode);
  const city: CascaderOption | undefined = province?.children?.find((item: CascaderOption): boolean => item.value === cityCode);
  const district: CascaderOption | undefined = city?.children?.find((item: CascaderOption): boolean => item.value === districtCode);
  if (!province || !city || !district) {
    return null;
  }
  const result: RegionSelection = new RegionSelection();
  result.provinceCode = province.value;
  result.cityCode = city.value;
  result.districtCode = district.value;
  result.province = province.text;
  result.city = city.text;
  result.district = district.text;
  return result;
}

export function findRegion(provinceText: string, cityText: string, districtText: string): RegionSelection {
  for (const province of addressRegions) {
    if (province.text !== provinceText) {
      continue;
    }
    for (const city of province.children ?? []) {
      if (city.text !== cityText) {
        continue;
      }
      for (const district of city.children ?? []) {
        if (district.text === districtText) {
          return resolveRegion(province.value, city.value, district.value) ?? new RegionSelection();
        }
      }
    }
  }
  return new RegionSelection();
}
