import { BaseViewModel } from "base";
import { GoodsRepository, SearchHistoryRepository } from "data";
import { GoodsSearchKeyword, SearchHistory } from "model";
import { GoodsNavigator } from "navigation";
import { RequestHelper } from "result";

/**
 * 搜索历史最多展示条数
 */
const MAX_HISTORY_COUNT: number = 10;

/**
 * @file 商品搜索页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class GoodsSearchViewModel extends BaseViewModel {
  /**
   * 商品仓库
   */
  private readonly goodsRepository: GoodsRepository = new GoodsRepository();
  /**
   * 搜索历史仓库
   */
  private readonly searchHistoryRepository: SearchHistoryRepository = new SearchHistoryRepository();
  /**
   * 搜索框输入内容
   */
  @Trace
  keyword: string = "";
  /**
   * 搜索历史关键词列表（按搜索时间倒序，最多 10 条）
   */
  @Trace
  historyList: string[] = [];
  /**
   * 推荐搜索关键词列表
   */
  @Trace
  recommendList: GoodsSearchKeyword[] = [];
  /**
   * 清空历史确认弹窗显示状态
   */
  @Trace
  showClearDialog: boolean = false;
  /**
   * 是否正在提交搜索（跳转结果页后锁定，页面重新显示时释放，防止连点重复跳转）
   */
  private isSubmitting: boolean = false;

  /**
   * 页面出现时加载搜索历史与推荐关键词
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    this.loadSearchHistory();
    this.loadRecommendKeywords();
  }

  /**
   * 页面显示时（含从结果页返回）释放提交锁并刷新搜索历史
   * @param {VisibilityChangeReason} reason - 可见性变化原因
   * @returns {void} 无返回值
   */
  onShown(reason: VisibilityChangeReason): void {
    this.isSubmitting = false;
    this.loadSearchHistory();
  }

  /**
   * 加载最近的搜索历史
   * @returns {void} 无返回值
   */
  loadSearchHistory(): void {
    this.searchHistoryRepository.getRecentSearchHistory(MAX_HISTORY_COUNT)
      .then((list: SearchHistory[]): void => {
        this.historyList = list.map((item: SearchHistory): string => item.keyword);
      })
      .catch((err: Error): void => {
        console.error("[GoodsSearchViewModel] load history error:", err?.message);
      });
  }

  /**
   * 加载推荐搜索关键词（失败或为空时只保留区域标题）
   * @returns {void} 无返回值
   */
  loadRecommendKeywords(): void {
    RequestHelper.repository<GoodsSearchKeyword[]>(this.goodsRepository.getSearchKeywordList())
      .toast(false)
      .execute()
      .then((data: GoodsSearchKeyword[]): void => {
        this.recommendList = data ?? [];
      })
      .catch((): void => {
        this.recommendList = [];
      });
  }

  /**
   * 更新搜索框输入内容
   * @param {string} value - 输入内容
   * @returns {void} 无返回值
   */
  updateKeyword(value: string): void {
    this.keyword = value;
  }

  /**
   * 使用搜索框当前内容执行搜索
   * @returns {boolean} 是否执行了搜索（去除首尾空格后为空时返回 false）
   */
  searchByInput(): boolean {
    return this.search(this.keyword);
  }

  /**
   * 点击历史或推荐关键词：填入搜索框并立即搜索
   * @param {string} word - 关键词
   * @returns {void} 无返回值
   */
  searchByTag(word: string): void {
    if (this.isSubmitting) {
      return;
    }
    this.keyword = word;
    this.search(word);
  }

  /**
   * 执行搜索：去除首尾空格后保存历史并跳转商品分类列表页
   * @param {string} word - 原始关键词
   * @returns {boolean} 是否执行了搜索
   */
  private search(word: string): boolean {
    const trimmed: string = word.trim();
    if (!trimmed) {
      return false;
    }
    if (this.isSubmitting) {
      return true;
    }
    this.isSubmitting = true;
    this.searchHistoryRepository.addSearchHistory(trimmed)
      .catch((err: Error): void => {
        console.error("[GoodsSearchViewModel] save history error:", err?.message);
      })
      .finally((): void => {
        GoodsNavigator.toCategory({ keyword: trimmed });
      });
    return true;
  }

  /**
   * 显示清空历史确认弹窗
   * @returns {void} 无返回值
   */
  showClearDialogModal(): void {
    this.showClearDialog = true;
  }

  /**
   * 隐藏清空历史确认弹窗
   * @returns {void} 无返回值
   */
  hideClearDialogModal(): void {
    this.showClearDialog = false;
  }

  /**
   * 确认清空所有搜索历史，并清空搜索框
   * @returns {void} 无返回值
   */
  confirmClearHistory(): void {
    this.searchHistoryRepository.clearAllSearchHistory()
      .then((): void => {
        this.historyList = [];
        this.keyword = "";
        this.hideClearDialogModal();
      })
      .catch((): void => {
        this.hideClearDialogModal();
        this.loadSearchHistory();
      });
  }
}
