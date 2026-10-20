import { GoodsNetworkDataSource } from "network";
import { Category, Comment, Goods, GoodsCommentPageRequest, GoodsCommentSubmitRequest, GoodsIdRequest,
  GoodsSearchKeyword, GoodsSearchRequest, GoodsSpec, NetworkPageData, NetworkPageMeta, NetworkResponse } from "model";
import { FixtureRequestQueue } from "./FixtureProtocol";

function fixtureResponse<T>(data: T | null, code: number = 1000, message: string | null = null): NetworkResponse<T> {
  const response: NetworkResponse<T> = new NetworkResponse<T>();
  response.code = code;
  response.message = message;
  response.data = data;
  return response;
}

/** Test-source-set IO substitute. All completion requires an explicit queue action. */
export class ControlledGoodsDataSource implements GoodsNetworkDataSource {
  private queue: FixtureRequestQueue;
  private instanceId: number;
  private scenario: string;
  private readonly image: string = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=";

  constructor(queue: FixtureRequestQueue, instanceId: number, scenario: string) {
    this.queue = queue;
    this.instanceId = instanceId;
    this.scenario = scenario;
  }

  getGoodsTypeList(): Promise<NetworkResponse<Category[]>> {
    return this.queue.enqueue<Category[]>(this.instanceId, this.scenario, "categories", undefined,
      (result: string): NetworkResponse<Category[]> => {
        if (result === "business") { return fixtureResponse<Category[]>(null, 4100, "fixture categories unavailable"); }
        const categories: Category[] = result === "empty" ? [] : [
          this.makeCategory(900001, "夹具分组一"),
          this.makeCategory(910001, "运动户外", 900001),
          this.makeCategory(910002, "数码", 900001),
          this.makeCategory(900002, "夹具分组二"),
          this.makeCategory(920001, "家居", 900002)
        ];
        return fixtureResponse<Category[]>(categories);
      }, (items: Category[] | null): number[] => (items ?? []).map((item: Category): number => item.id));
  }

  getGoodsPage(params: GoodsSearchRequest): Promise<NetworkResponse<NetworkPageData<Goods>>> {
    const request: GoodsSearchRequest = new GoodsSearchRequest(params);
    request.typeId = params.typeId?.slice();
    return this.queue.enqueue<NetworkPageData<Goods>>(this.instanceId, this.scenario, "goods", request,
      (result: string): NetworkResponse<NetworkPageData<Goods>> => this.goodsResponse(request, result),
      (data: NetworkPageData<Goods> | null): number[] => (data?.list ?? []).map((item: Goods): number => item.id));
  }

  private goodsResponse(request: GoodsSearchRequest, result: string): NetworkResponse<NetworkPageData<Goods>> {
    if (result === "business") {
      return fixtureResponse<NetworkPageData<Goods>>(null, 4100, "fixture goods unavailable");
    }
    let goods: Goods[] = result === "empty" || this.scenario === "empty" ? [] : this.makeGoods();
    const keyword: string = request.keyWord?.trim().toLowerCase() ?? "";
    goods = goods.filter((item: Goods): boolean =>
      (keyword.length === 0 || item.title.toLowerCase().includes(keyword)) &&
      (request.typeId === undefined || request.typeId === null || request.typeId.length === 0 || request.typeId.includes(item.typeId)) &&
      (request.minPrice === undefined || request.minPrice === null || item.price > Number(request.minPrice)) &&
      (request.maxPrice === undefined || request.maxPrice === null || item.price <= Number(request.maxPrice)) &&
      (request.featured === undefined || item.featured === request.featured) &&
      (request.recommend === undefined || item.recommend === request.recommend));
    if (request.order === "price" || request.order === "sold") {
      const direction: number = request.sort === "desc" ? -1 : 1;
      goods.sort((left: Goods, right: Goods): number => direction *
        (request.order === "price" ? left.price - right.price : left.sold - right.sold));
    }
    const total: number = goods.length;
    const list: Goods[] = goods.slice((request.page - 1) * request.size, request.page * request.size);
    const pagination: NetworkPageMeta = new NetworkPageMeta();
    pagination.page = result === "wrongPage" ? request.page + 1 : request.page;
    pagination.size = request.size;
    pagination.total = total;
    const data: NetworkPageData<Goods> = new NetworkPageData<Goods>();
    data.list = list;
    data.pagination = result === "missingMeta" || this.scenario === "missingMeta" ? null : pagination;
    return fixtureResponse<NetworkPageData<Goods>>(data);
  }

  private makeCategory(id: number, name: string, parentId: number | null = null): Category {
    const category: Category = new Category();
    category.id = id;
    category.name = name;
    category.parentId = parentId;
    return category;
  }

  private makeGoods(): Goods[] {
    const total: number = this.scenario === "fullEnd" ? 40 : 45;
    const goods: Goods[] = [];
    const types: number[] = [910001, 910002, 920001];
    for (let index: number = 1; index <= total; index++) {
      const item: Goods = new Goods();
      item.id = 100000 + index;
      item.typeId = types[(index - 1) % types.length];
      item.title = `${index <= 30 ? "X" : "Y"} 商品 ${index.toString().padStart(2, "0")}`;
      item.mainPic = this.image;
      item.price = 10 + index * 3;
      item.sold = 1000 - index * 7;
      item.featured = index % 2 === 0;
      item.recommend = index % 3 === 0;
      goods.push(item);
    }
    return goods;
  }

  getGoodsSpecList(params: GoodsIdRequest): Promise<NetworkResponse<GoodsSpec[]>> {
    return Promise.reject(new Error("fixture unsupported getGoodsSpecList"));
  }
  getSearchKeywordList(): Promise<NetworkResponse<GoodsSearchKeyword[]>> {
    return Promise.reject(new Error("fixture unsupported getSearchKeywordList"));
  }
  getGoodsInfo(id: string): Promise<NetworkResponse<Goods>> {
    return Promise.reject(new Error("fixture unsupported getGoodsInfo"));
  }
  submitGoodsComment(params: GoodsCommentSubmitRequest): Promise<NetworkResponse<boolean>> {
    return Promise.reject(new Error("fixture unsupported submitGoodsComment"));
  }
  getGoodsCommentPage(params: GoodsCommentPageRequest): Promise<NetworkResponse<NetworkPageData<Comment>>> {
    return Promise.reject(new Error("fixture unsupported getGoodsCommentPage"));
  }
}
