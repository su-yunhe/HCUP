import { BaseNetWorkViewModel } from "base";
import { GoodsRepository, SearchHistoryRepository } from "data";
import { GoodsSearchKeyword, NetworkResponse, SearchHistory } from "model";
import { GoodsNavigator } from "navigation";
import { GoodsCategoryParam } from "navigation/src/main/ets/goods/GoodsParam";

/**
 * @file 商品搜索页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class GoodsSearchViewModel extends BaseNetWorkViewModel<GoodsSearchKeyword[]> {
  /**
   * 商品仓库
   */
  private readonly goodsRepository: GoodsRepository = new GoodsRepository();
  /**
   * 搜索历史仓库
   */
  private readonly searchHistoryRepository: SearchHistoryRepository = new SearchHistoryRepository();
  /**
   * 搜索关键字
   */
  @Trace
  searchValue: string = "";
  /**
   * 搜索历史列表
   */
  @Trace
  searchHistoryList: SearchHistory[] = [];
  /**
   * 是否显示清空搜索历史确认弹窗
   */
  @Trace
  isClearHistoryDialogVisible: boolean = false;

  /**
   * 页面出现时加载数据
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    this.loadSearchHistory();
    super.aboutToAppear();
  }

  /**
   * 请求推荐搜索关键词列表
   * @returns {Promise<NetworkResponse<GoodsSearchKeyword[]>>} 网络请求 Promise
   */
  protected requestRepository(): Promise<NetworkResponse<GoodsSearchKeyword[]>> {
    return this.goodsRepository.getSearchKeywordList();
  }

  /**
   * 输入变化回调
   * @param {string} value - 输入内容
   * @returns {void} 无返回值
   */
  onSearchValueChange(value: string): void {
    this.searchValue = value;
  }

  /**
   * 搜索提交
   * @returns {void} 无返回值
   */
  onSearchSubmit(): void {
    this.onSearch(this.searchValue);
  }

  /**
   * 执行搜索
   * @param {string} keyword - 搜索关键词
   * @returns {Promise<void>} Promise<void>
   */
  async onSearch(keyword: string): Promise<void> {
    const trimmed: string = keyword.trim();
    if (!trimmed) {
      return;
    }
    this.searchValue = trimmed;
    await this.searchHistoryRepository.addSearchHistory(trimmed);
    await this.loadSearchHistory();

    const params: GoodsCategoryParam = {
      featured: false,
      recommend: false,
      keyword: trimmed
    };
    GoodsNavigator.toCategory(params);
  }

  /**
   * 点击推荐关键词
   * @param {string} keyword - 关键词
   * @returns {void} 无返回值
   */
  async onKeywordClick(keyword: string): Promise<void> {
    await this.onSearch(keyword);
  }

  /**
   * 点击搜索历史
   * @param {SearchHistory} searchHistory - 搜索历史
   * @returns {void} 无返回值
   */
  async onSearchHistoryClick(searchHistory: SearchHistory): Promise<void> {
    await this.onSearch(searchHistory.keyword);
  }

  /**
   * 点击清空搜索历史
   * @returns {void} 无返回值
   */
  clearSearchHistory(): void {
    this.showClearHistoryDialog();
  }

  /**
   * 显示清空搜索历史确认弹窗
   * @returns {void} 无返回值
   */
  showClearHistoryDialog(): void {
    this.isClearHistoryDialogVisible = true;
  }

  /**
   * 隐藏清空搜索历史确认弹窗
   * @returns {void} 无返回值
   */
  hideClearHistoryDialog(): void {
    this.isClearHistoryDialogVisible = false;
  }

  /**
   * 确认清空搜索历史
   * @returns {void} 无返回值
   */
  confirmClearSearchHistory(): void {
    this.handleClearHistory();
  }

  /**
   * 加载搜索历史列表
   * @returns {void} 无返回值
   */
  private async loadSearchHistory(): Promise<void> {
    this.searchHistoryList = await this.searchHistoryRepository.getRecentSearchHistory(10);
  }

  /**
   * 清空搜索历史并刷新列表
   * @returns {Promise<void>} Promise<void>
   */
  private async handleClearHistory(): Promise<void> {
    await this.searchHistoryRepository.clearAllSearchHistory();
    this.hideClearHistoryDialog();
    await this.loadSearchHistory();
  }
}
