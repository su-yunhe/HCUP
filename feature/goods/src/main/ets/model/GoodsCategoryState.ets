export enum GoodsCategorySort {
  DEFAULT = "default", PRICE_ASC = "priceAsc", PRICE_DESC = "priceDesc", SOLD_ASC = "soldAsc", SOLD_DESC = "soldDesc"
}

export enum GoodsCategoryLoadPhase {
  IDLE = "idle", FIRST = "first", REFRESH = "refresh", MORE = "more"
}

/** Immutable snapshots are copied before each request. */
export class GoodsCategoryQuery {
  keyword?: string;
  typeIds: number[] = [];
  minPrice?: string;
  maxPrice?: string;
  featured?: boolean;
  recommend?: boolean;
  sortMode: GoodsCategorySort = GoodsCategorySort.DEFAULT;

  copy(): GoodsCategoryQuery {
    const result: GoodsCategoryQuery = new GoodsCategoryQuery();
    result.keyword = this.keyword;
    result.typeIds = this.typeIds.slice();
    result.minPrice = this.minPrice;
    result.maxPrice = this.maxPrice;
    result.featured = this.featured;
    result.recommend = this.recommend;
    result.sortMode = this.sortMode;
    return result;
  }

  equals(other: GoodsCategoryQuery): boolean {
    return this.keyword === other.keyword && this.minPrice === other.minPrice &&
      this.maxPrice === other.maxPrice && this.featured === other.featured &&
      this.recommend === other.recommend && this.sortMode === other.sortMode &&
      this.typeIds.length === other.typeIds.length &&
      this.typeIds.every((id: number): boolean => other.typeIds.includes(id));
  }
}

export class GoodsCategoryTag {
  id: number;
  name: string;
  constructor(id: number, name: string) { this.id = id; this.name = name; }
}

export class GoodsCategoryGroup {
  id: number;
  name: string;
  tags: GoodsCategoryTag[];
  constructor(id: number, name: string, tags: GoodsCategoryTag[]) {
    this.id = id; this.name = name; this.tags = tags;
  }
}

export class GoodsCategoryRequestStamp {
  lifeEpoch: number;
  queryVersion: number;
  requestId: number;
  page: number;
  kind: GoodsCategoryLoadPhase;
  query: GoodsCategoryQuery;
  constructor(epoch: number, version: number, id: number, page: number,
    kind: GoodsCategoryLoadPhase, query: GoodsCategoryQuery) {
    this.lifeEpoch = epoch; this.queryVersion = version; this.requestId = id;
    this.page = page; this.kind = kind; this.query = query.copy();
  }
}
