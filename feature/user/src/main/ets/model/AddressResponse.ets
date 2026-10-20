import { Address } from "model";

// Validate raw fields before model defaults can conceal malformed responses.
export function isAddress(value: Address | null | undefined): boolean {
  return value !== null && value !== undefined && Number.isInteger(value.id) && value.id > 0 &&
    typeof value.contact === "string" && typeof value.phone === "string" &&
    typeof value.province === "string" && typeof value.city === "string" &&
    typeof value.district === "string" && typeof value.address === "string" &&
    typeof value.isDefault === "boolean";
}

export function addressError(error: Object): string {
  return error instanceof Error ? error.message : "网络异常，请稍后重试";
}

export function sameAddressFields(left: Address, right: Address): boolean {
  return left.contact === right.contact && left.phone === right.phone &&
    left.province === right.province && left.city === right.city &&
    left.district === right.district && left.address === right.address &&
    left.isDefault === right.isDefault;
}
