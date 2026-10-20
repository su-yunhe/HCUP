import { BaseNetWorkListUiState, BaseViewModel } from "base";
import { GoodsRepository } from "data";
import { Category, Goods, GoodsSearchRequest, NetworkPageData, NetworkPageMeta } from "model";
import { GoodsCategoryParam } from "navigation/src/main/ets/goods/GoodsParam";
import { RequestHelper } from "result";
import {
  GoodsCategoryGroup, GoodsCategoryLoadPhase, GoodsCategoryQuery, GoodsCategoryRequestStamp,
  GoodsCategorySort, GoodsCategoryTag
} from "../model/GoodsCategoryState";

/** Owns the query, draft and versioned requests of one destination instance. */
@ObservedV2
export default class GoodsCategoryViewModel extends BaseViewModel {
  @Trace searchValue: string = "";
  @Trace query: GoodsCategoryQuery = new GoodsCategoryQuery();
  @Trace listData: Goods[] = [];
  @Trace uiState: BaseNetWorkListUiState = BaseNetWorkListUiState.LOADING;
  @Trace phase: GoodsCategoryLoadPhase = GoodsCategoryLoadPhase.IDLE;
  @Trace hasMore: boolean = false;
  @Trace isGridMode: boolean = true;
  @Trace filterVisible: boolean = false;
  @Trace sortVisible: boolean = false;
  @Trace sortTouched: boolean = false;
  @Trace draftTypeIds: number[] = [];
  @Trace draftMinPrice: string = "";
  @Trace draftMaxPrice: string = "";
  @Trace filterError: string = "";
  @Trace errorMessage: string = "";
  @Trace moreError: string = "";
  @Trace refreshError: string = "";
  @Trace categoryGroups: GoodsCategoryGroup[] = [];
  @Trace categoriesLoading: boolean = false;
  @Trace categoriesError: string = "";
  @Trace scrollRevision: number = 0;
  committedPage: number = 0;
  readonly pageSize: number = 20;
  readonly sortOptions: GoodsCategorySort[] = [GoodsCategorySort.DEFAULT, GoodsCategorySort.PRICE_ASC,
    GoodsCategorySort.PRICE_DESC, GoodsCategorySort.SOLD_ASC, GoodsCategorySort.SOLD_DESC];
  private readonly repository: GoodsRepository;
  private initialized: boolean = false;
  private active: boolean = true;
  private lifeEpoch: number = 1;
  private queryVersion: number = 0;
  private requestSequence: number = 0;
  private currentRequestId: number = 0;
  private categoryRequestId: number = 0;
  private categoriesLoaded: boolean = false;
  private reloadNeeded: boolean = false;
  private entryTypeId?: number;
  private waitingForEntry: boolean = false;
  private categoryNodes: Map<number, Category> = new Map();

  constructor(repository?: GoodsRepository) {
    super();
    this.repository = repository ?? new GoodsRepository();
  }

  get isLoading(): boolean { return this.phase !== GoodsCategoryLoadPhase.IDLE; }
  get hasAppliedFilter(): boolean {
    return this.query.typeIds.length > 0 || this.query.minPrice !== undefined || this.query.maxPrice !== undefined;
  }
  get sortTitle(): string { return this.sortTouched ? this.sortLabel(this.query.sortMode) : "排序"; }
  sortLabel(mode: GoodsCategorySort): string {
    switch (mode) {
      case GoodsCategorySort.PRICE_ASC: return "价格由低到高";
      case GoodsCategorySort.PRICE_DESC: return "价格由高到低";
      case GoodsCategorySort.SOLD_ASC: return "销量由低到高";
      case GoodsCategorySort.SOLD_DESC: return "销量由高到低";
      default: return "综合排序";
    }
  }

  initialize(params?: GoodsCategoryParam): void {
    if (this.initialized) { return; }
    this.initialized = true;
    const initial: GoodsCategoryQuery = new GoodsCategoryQuery();
    const keyword: string = params?.keyword?.trim() ?? "";
    initial.keyword = keyword.length > 0 ? keyword : undefined;
    initial.featured = params?.featured;
    initial.recommend = params?.recommend;
    const minimum: string = params?.minPrice?.trim() ?? "";
    if (minimum.length > 0 && this.validAmount(minimum)) { initial.minPrice = minimum; }
    const typeText: string = params?.typeId?.trim() ?? "";
    const typeId: number = Number(typeText);
    if (/^\d+$/.test(typeText) && Number.isSafeInteger(typeId) && typeId > 0) {
      this.entryTypeId = typeId;
      this.waitingForEntry = true;
      initial.typeIds = [typeId];
    }
    this.query = initial;
    this.searchValue = keyword;
    void this.loadCategories();
    if (!this.waitingForEntry) { this.reload(GoodsCategoryLoadPhase.FIRST); }
  }

  onSearchValueChange(value: string): void { this.searchValue = value; }
  submitSearch(value: string = this.searchValue): void {
    const trimmed: string = value.trim();
    if (trimmed.length === 0) { return; }
    this.searchValue = trimmed;
    this.closeMenus();
    const next: GoodsCategoryQuery = this.query.copy();
    next.keyword = trimmed;
    this.applyQuery(next);
  }

  openFilter(): void {
    if (this.filterVisible) { this.closeMenus(); return; }
    this.closeMenus();
    this.draftTypeIds = this.query.typeIds.slice();
    this.draftMinPrice = this.query.minPrice ?? "";
    this.draftMaxPrice = this.query.maxPrice ?? "";
    this.filterVisible = true;
  }
  openSort(): void {
    const show: boolean = !this.sortVisible;
    this.closeMenus();
    this.sortVisible = show;
  }
  closeMenus(): boolean {
    const consumed: boolean = this.filterVisible || this.sortVisible;
    this.filterVisible = false;
    this.sortVisible = false;
    this.draftTypeIds = [];
    this.draftMinPrice = "";
    this.draftMaxPrice = "";
    this.filterError = "";
    return consumed;
  }
  toggleCategory(id: number): void {
    this.draftTypeIds = this.draftTypeIds.includes(id) ?
      this.draftTypeIds.filter((value: number): boolean => value !== id) : [...this.draftTypeIds, id];
  }
  resetDraft(): void {
    this.draftTypeIds = [];
    this.draftMinPrice = "";
    this.draftMaxPrice = "";
    this.filterError = "";
  }
  confirmFilter(): void {
    if (!this.filterVisible) { return; }
    if (this.waitingForEntry && this.entryTypeId !== undefined && this.draftTypeIds.includes(this.entryTypeId)) {
      this.filterError = this.categoriesLoading ? "分类加载中，请稍后确认" : "请先重试加载分类";
      return;
    }
    const minimum: string = this.draftMinPrice.trim();
    const maximum: string = this.draftMaxPrice.trim();
    if ((minimum.length > 0 && !this.validAmount(minimum)) || (maximum.length > 0 && !this.validAmount(maximum))) {
      this.filterError = "请输入有效的非负金额";
      return;
    }
    if (minimum.length > 0 && maximum.length > 0 && Number(minimum) > Number(maximum)) {
      this.filterError = "最低价不能高于最高价";
      return;
    }
    const next: GoodsCategoryQuery = this.query.copy();
    next.typeIds = this.draftTypeIds.slice();
    next.minPrice = minimum.length > 0 ? minimum : undefined;
    next.maxPrice = maximum.length > 0 ? maximum : undefined;
    // A confirmed editable filter supersedes the entrance, including an unresolved root.
    this.entryTypeId = undefined;
    this.waitingForEntry = false;
    this.closeMenus();
    this.applyQuery(next);
  }
  selectSort(mode: GoodsCategorySort): void {
    this.closeMenus();
    this.sortTouched = true;
    if (mode === this.query.sortMode) {
      if (this.uiState === BaseNetWorkListUiState.ERROR) { this.retryRequest(); }
      return;
    }
    const next: GoodsCategoryQuery = this.query.copy();
    next.sortMode = mode;
    this.applyQuery(next);
  }
  toggleLayout(): void { this.isGridMode = !this.isGridMode; }
  onRefresh(): void {
    if (!this.active || this.waitingForEntry || this.phase === GoodsCategoryLoadPhase.FIRST ||
      this.phase === GoodsCategoryLoadPhase.REFRESH) { return; }
    this.reload(this.listData.length > 0 ? GoodsCategoryLoadPhase.REFRESH : GoodsCategoryLoadPhase.FIRST);
  }
  onLoadMore(): void {
    if (!this.active || this.phase !== GoodsCategoryLoadPhase.IDLE || !this.hasMore || this.listData.length === 0) { return; }
    this.startRequest(this.committedPage + 1, GoodsCategoryLoadPhase.MORE);
  }
  retryRequest(): void {
    if (this.waitingForEntry) { void this.loadCategories(); }
    else if (!this.isLoading) { this.reload(GoodsCategoryLoadPhase.FIRST); }
  }
  retryCategories(): void { void this.loadCategories(); }
  private validAmount(value: string): boolean {
    return /^(\d+(\.\d*)?|\.\d+)$/.test(value) && Number.isFinite(Number(value)) && Number(value) >= 0;
  }
  private applyQuery(next: GoodsCategoryQuery): void {
    // Only merge duplicate first-page intent. A deliberate search/confirm during P2 must replace it.
    if (next.equals(this.query) && (this.phase === GoodsCategoryLoadPhase.FIRST ||
      this.phase === GoodsCategoryLoadPhase.REFRESH)) { return; }
    this.query = next.copy();
    this.reload(GoodsCategoryLoadPhase.FIRST);
  }
  private reload(kind: GoodsCategoryLoadPhase): void {
    if (!this.active) { this.reloadNeeded = true; return; }
    if (this.waitingForEntry) { return; }
    this.queryVersion++;
    if (kind === GoodsCategoryLoadPhase.FIRST) {
      this.listData = [];
      this.committedPage = 0;
      this.hasMore = false;
      this.uiState = BaseNetWorkListUiState.LOADING;
    }
    this.startRequest(1, kind);
  }
  private startRequest(page: number, kind: GoodsCategoryLoadPhase): void {
    const stamp: GoodsCategoryRequestStamp = new GoodsCategoryRequestStamp(this.lifeEpoch,
      this.queryVersion, ++this.requestSequence, page, kind, this.query);
    this.currentRequestId = stamp.requestId;
    this.phase = kind;
    this.errorMessage = "";
    this.moreError = "";
    this.refreshError = "";
    this.logRequest("start", stamp);
    void this.executeRequest(stamp);
  }
  private makeRequest(stamp: GoodsCategoryRequestStamp): GoodsSearchRequest {
    const request: GoodsSearchRequest = new GoodsSearchRequest();
    request.page = stamp.page;
    request.size = this.pageSize;
    const query: GoodsCategoryQuery = stamp.query;
    if (query.keyword !== undefined) { request.keyWord = query.keyword; }
    if (query.typeIds.length > 0) { request.typeId = query.typeIds.slice(); }
    if (query.minPrice !== undefined) { request.minPrice = query.minPrice; }
    if (query.maxPrice !== undefined) { request.maxPrice = query.maxPrice; }
    if (query.featured !== undefined) { request.featured = query.featured; }
    if (query.recommend !== undefined) { request.recommend = query.recommend; }
    switch (query.sortMode) {
      case GoodsCategorySort.PRICE_ASC: request.order = "price"; request.sort = "asc"; break;
      case GoodsCategorySort.PRICE_DESC: request.order = "price"; request.sort = "desc"; break;
      case GoodsCategorySort.SOLD_ASC: request.order = "sold"; request.sort = "asc"; break;
      case GoodsCategorySort.SOLD_DESC: request.order = "sold"; request.sort = "desc"; break;
      default: break;
    }
    return request;
  }
  private isCurrent(stamp: GoodsCategoryRequestStamp): boolean {
    return this.active && stamp.lifeEpoch === this.lifeEpoch && stamp.queryVersion === this.queryVersion &&
      stamp.requestId === this.currentRequestId;
  }
  private async executeRequest(stamp: GoodsCategoryRequestStamp): Promise<void> {
    try {
      const data: NetworkPageData<Goods> = await RequestHelper.repository<NetworkPageData<Goods>>(
        this.repository.getGoodsPage(this.makeRequest(stamp))).toast(false).execute();
      if (!this.isCurrent(stamp)) { this.logRequest("discard-success", stamp); return; }
      const metadata: NetworkPageMeta | null = data?.pagination ?? null;
      if (metadata?.page !== undefined && metadata.page !== null && metadata.page !== stamp.page) {
        throw new Error("返回页码不匹配，请重试");
      }
      if (stamp.kind === GoodsCategoryLoadPhase.MORE && stamp.page !== this.committedPage + 1) {
        throw new Error("分页状态已改变，请重试");
      }
      const raw: Goods[] = data?.list ?? [];
      const previous: Goods[] = stamp.page === 1 ? [] : this.listData;
      const ids: Set<number> = new Set(previous.map((item: Goods): number => item.id));
      const added: Goods[] = [];
      raw.forEach((item: Goods): void => {
        if (!ids.has(item.id)) { ids.add(item.id); added.push(item); }
      });
      this.listData = [...previous, ...added];
      this.committedPage = stamp.page;
      this.hasMore = raw.length > 0 && added.length > 0 && this.calculateHasMore(metadata, stamp.page, raw.length);
      this.uiState = this.listData.length > 0 ? BaseNetWorkListUiState.SUCCESS : BaseNetWorkListUiState.EMPTY;
      if (stamp.page === 1) { this.scrollRevision++; }
      this.logRequest("commit", stamp);
    } catch (error) {
      if (!this.isCurrent(stamp)) { this.logRequest("discard-error", stamp); return; }
      const message: string = error instanceof Error ? error.message : "网络异常，请重试";
      if (stamp.kind === GoodsCategoryLoadPhase.MORE) { this.moreError = message; }
      else if (stamp.kind === GoodsCategoryLoadPhase.REFRESH && this.listData.length > 0) { this.refreshError = message; }
      else { this.errorMessage = message; this.uiState = BaseNetWorkListUiState.ERROR; }
      this.logRequest("error", stamp);
    } finally {
      if (this.isCurrent(stamp)) {
        this.phase = GoodsCategoryLoadPhase.IDLE;
        this.currentRequestId = 0;
        this.logRequest("finish", stamp);
      }
    }
  }
  private calculateHasMore(meta: NetworkPageMeta | null, page: number, rawSize: number): boolean {
    if (meta !== null && meta.total !== null && meta.size !== null && meta.page !== null &&
      Number.isFinite(meta.total) && meta.total >= 0 && Number.isFinite(meta.size) && meta.size > 0 &&
      Number.isFinite(meta.page) && meta.page === page) { return meta.page * meta.size < meta.total; }
    return rawSize >= this.pageSize;
  }
  private logRequest(event: string, stamp: GoodsCategoryRequestStamp): void {
    console.info(`[GoodsCategory] event=${event} id=${stamp.requestId} version=${stamp.queryVersion} ` +
      `epoch=${stamp.lifeEpoch} kind=${stamp.kind} page=${stamp.page}`);
  }

  private async loadCategories(): Promise<void> {
    if (!this.active || this.categoriesLoading || this.categoriesLoaded) { return; }
    const requestId: number = ++this.categoryRequestId;
    const epoch: number = this.lifeEpoch;
    this.categoriesLoading = true;
    this.categoriesError = "";
    try {
      const categories: Category[] = await RequestHelper.repository<Category[]>(
        this.repository.getGoodsTypeList()).toast(false).execute();
      if (!this.active || requestId !== this.categoryRequestId || epoch !== this.lifeEpoch) { return; }
      this.normalizeCategories(categories ?? []);
      this.categoriesLoaded = true;
      if (this.waitingForEntry && this.entryTypeId !== undefined) {
        const leaves: Category[] = this.collectLeaves(this.entryTypeId, [], new Set<number>());
        const next: GoodsCategoryQuery = this.query.copy();
        next.typeIds = leaves.length > 0 ? leaves.map((item: Category): number => item.id) : [this.entryTypeId];
        if (this.filterVisible && this.draftTypeIds.includes(this.entryTypeId)) {
          const entrance: number = this.entryTypeId;
          this.draftTypeIds = [...this.draftTypeIds.filter((id: number): boolean => id !== entrance), ...next.typeIds];
          this.filterError = "";
        }
        this.query = next;
        this.entryTypeId = undefined;
        this.waitingForEntry = false;
        this.reload(GoodsCategoryLoadPhase.FIRST);
      }
    } catch (error) {
      if (!this.active || requestId !== this.categoryRequestId || epoch !== this.lifeEpoch) { return; }
      this.categoriesError = "分类加载失败，请重试";
      if (this.waitingForEntry) {
        this.errorMessage = this.categoriesError;
        this.uiState = BaseNetWorkListUiState.ERROR;
      }
    } finally {
      if (this.active && requestId === this.categoryRequestId && epoch === this.lifeEpoch) { this.categoriesLoading = false; }
    }
  }
  private addCategories(items: Category[], parentId: number | undefined, path: number[]): void {
    items.forEach((item: Category): void => {
      if (!Number.isSafeInteger(item.id) || item.id <= 0 || path.includes(item.id)) { return; }
      if (!this.categoryNodes.has(item.id)) {
        const node: Category = new Category(item);
        node.parentId = item.parentId ?? parentId ?? null;
        node.children = [];
        this.categoryNodes.set(item.id, node);
      }
      this.addCategories(item.children ?? [], item.id, [...path, item.id]);
    });
  }
  private childrenOf(id: number): Category[] {
    const children: Category[] = [];
    this.categoryNodes.forEach((item: Category): void => {
      if (item.parentId === id && item.id !== id) { children.push(item); }
    });
    return children.sort((left: Category, right: Category): number => left.sortNum - right.sortNum);
  }
  private collectLeaves(id: number, path: number[], visited: Set<number>): Category[] {
    if (path.includes(id)) { return []; }
    const node: Category | undefined = this.categoryNodes.get(id);
    if (node === undefined) { return []; }
    visited.add(id);
    const children: Category[] = this.childrenOf(id);
    if (children.length === 0) { return [node]; }
    let result: Category[] = [];
    children.forEach((child: Category): void => {
      result = [...result, ...this.collectLeaves(child.id, [...path, id], visited)];
    });
    return result;
  }
  private normalizeCategories(items: Category[]): void {
    this.categoryNodes = new Map();
    this.addCategories(items, undefined, []);
    const ordered: Category[] = [];
    this.categoryNodes.forEach((item: Category): void => { ordered.push(item); });
    ordered.sort((left: Category, right: Category): number => left.sortNum - right.sortNum);
    const roots: Category[] = ordered.filter((item: Category): boolean => item.parentId === null ||
      item.parentId === undefined || item.parentId === item.id || !this.categoryNodes.has(item.parentId));
    const visited: Set<number> = new Set();
    const groups: GoodsCategoryGroup[] = [];
    // The second pass includes malformed/orphan cycles without recursive loops or invented labels.
    [...roots, ...ordered].forEach((root: Category): void => {
      if (visited.has(root.id)) { return; }
      const leaves: Category[] = this.collectLeaves(root.id, [], visited);
      const ids: Set<number> = new Set();
      const tags: GoodsCategoryTag[] = [];
      (leaves.length > 0 ? leaves : [root]).forEach((leaf: Category): void => {
        if (!ids.has(leaf.id)) { ids.add(leaf.id); tags.push(new GoodsCategoryTag(leaf.id, leaf.name)); }
      });
      groups.push(new GoodsCategoryGroup(root.id, root.name, tags));
    });
    this.categoryGroups = groups;
  }
  private deactivate(): void {
    if (!this.active) { return; }
    this.reloadNeeded = this.isLoading || this.waitingForEntry;
    this.active = false;
    this.lifeEpoch++;
    this.currentRequestId = 0;
    this.categoryRequestId++;
    this.phase = GoodsCategoryLoadPhase.IDLE;
    this.categoriesLoading = false;
    this.closeMenus();
  }
  onHidden(reason: VisibilityChangeReason): void { this.deactivate(); }
  aboutToDisappear(): void { this.deactivate(); }
  aboutToBeDeleted(): void { this.deactivate(); }
  onShown(reason: VisibilityChangeReason): void {
    if (!this.initialized || this.active) { return; }
    this.active = true;
    if (!this.categoriesLoaded) { void this.loadCategories(); }
    if (this.reloadNeeded) { this.reloadNeeded = false; this.reload(GoodsCategoryLoadPhase.FIRST); }
  }
}
