import { getORM } from "@ibestservices/ibest-orm";
import { SearchHistory } from "model";
import { SearchHistoryRow } from "../../model/SearchHistoryRow";
import { SearchHistoryTableInfo } from "../../model/SearchHistoryTableInfo";
import { SearchHistoryLocalDataSource } from "./SearchHistoryLocalDataSource";

/**
 * @file 搜索历史本地数据源实现
 * @author Joker.X
 */
export class SearchHistoryLocalDataSourceImpl implements SearchHistoryLocalDataSource {
  /**
   * 表名
   */
  private static readonly TABLE_NAME: string = "search_history";
  /**
   * 迁移标记，防止重复执行
   */
  private static migrated: boolean = false;
  /**
   * ORM 实例，用于执行数据库操作
   */
  private orm = getORM();

  /**
   * 构造函数，初始化 ORM 并确保搜索历史表已就绪
   * @returns {SearchHistoryLocalDataSourceImpl} 实例
   */
  constructor() {
    this.ensureMigrated();
  }

  /**
   * 确保搜索历史表准备完成
   * @returns {void} 无返回
   */
  private ensureMigrated(): void {
    if (SearchHistoryLocalDataSourceImpl.migrated) {
      return;
    }

    this.ensureTableSchema();
    SearchHistoryLocalDataSourceImpl.migrated = true;
  }

  /**
   * 确保搜索历史表结构正确
   * @returns {void} 无返回
   */
  private ensureTableSchema(): void {
    const tableName: string = SearchHistoryLocalDataSourceImpl.TABLE_NAME;

    if (!this.orm.hasTable(tableName)) {
      this.createSearchHistoryTable();
      return;
    }

    const tableInfo: SearchHistoryTableInfo[] = this.orm.getTableInfo(tableName) as SearchHistoryTableInfo[];
    const keywordColumn: SearchHistoryTableInfo | undefined = tableInfo.find((item: SearchHistoryTableInfo) => {
      return item.name === "keyword";
    });
    const keywordType: string = (keywordColumn?.type ?? "").toUpperCase();

    if (keywordType === "TEXT") {
      return;
    }

    this.orm.executeSql(`DROP TABLE IF EXISTS ${tableName}`);
    this.createSearchHistoryTable();
  }

  /**
   * 创建搜索历史表
   * @returns {void} 无返回
   */
  private createSearchHistoryTable(): void {
    this.orm.executeSql(
      `CREATE TABLE IF NOT EXISTS ${SearchHistoryLocalDataSourceImpl.TABLE_NAME} (keyword TEXT PRIMARY KEY, search_time INTEGER)`
    );
  }

  /**
   * 添加搜索历史记录
   * @param {SearchHistory} searchHistory 搜索历史记录
   * @returns {Promise<void>} Promise<void>
   */
  async addSearchHistory(searchHistory: SearchHistory): Promise<void> {
    const keyword: string = searchHistory.keyword.trim();
    if (!keyword) {
      return;
    }

    this.orm.table(SearchHistoryLocalDataSourceImpl.TABLE_NAME).where("keyword", keyword).delete();
    this.orm.table(SearchHistoryLocalDataSourceImpl.TABLE_NAME).insert({
      keyword: keyword,
      search_time: searchHistory.searchTime
    });
  }

  /**
   * 根据关键词删除搜索历史记录
   * @param {string} keyword 搜索关键词
   * @returns {Promise<void>} Promise<void>
   */
  async removeSearchHistory(keyword: string): Promise<void> {
    this.orm.table(SearchHistoryLocalDataSourceImpl.TABLE_NAME).where("keyword", keyword).delete();
  }

  /**
   * 清空所有搜索历史记录
   * @returns {Promise<void>} Promise<void>
   */
  async clearAllSearchHistory(): Promise<void> {
    this.orm.table(SearchHistoryLocalDataSourceImpl.TABLE_NAME).delete();
  }

  /**
   * 获取所有搜索历史记录，按搜索时间倒序
   * @returns {Promise<SearchHistory[]>} 搜索历史列表
   */
  async getAllSearchHistory(): Promise<SearchHistory[]> {
    const rows: SearchHistoryRow[] = this.orm.table(SearchHistoryLocalDataSourceImpl.TABLE_NAME).find() as SearchHistoryRow[];
    return rows
      .map((row: SearchHistoryRow) => this.toModel(row))
      .sort((left: SearchHistory, right: SearchHistory) => right.searchTime - left.searchTime);
  }

  /**
   * 获取搜索历史记录数量
   * @returns {Promise<number>} 搜索历史数量
   */
  async getSearchHistoryCount(): Promise<number> {
    return this.orm.table(SearchHistoryLocalDataSourceImpl.TABLE_NAME).count();
  }

  /**
   * 获取指定数量的最新搜索历史记录
   * @param {number} limit 限制数量
   * @returns {Promise<SearchHistory[]>} 搜索历史列表
   */
  async getRecentSearchHistory(limit: number): Promise<SearchHistory[]> {
    const all: SearchHistory[] = await this.getAllSearchHistory();
    return all.slice(0, limit);
  }

  /**
   * 根据关键词获取搜索历史记录
   * @param {string} keyword 搜索关键词
   * @returns {Promise<SearchHistory | undefined>} 匹配到的搜索历史
   */
  async getSearchHistoryByKeyword(keyword: string): Promise<SearchHistory | undefined> {
    const row: SearchHistoryRow | null = this.orm
      .table(SearchHistoryLocalDataSourceImpl.TABLE_NAME)
      .where("keyword", keyword)
      .first() as SearchHistoryRow | null;
    return row ? this.toModel(row) : undefined;
  }

  /**
   * 将数据库行数据转换为领域模型
   * @param {SearchHistoryRow} row 数据库行数据
   * @returns {SearchHistory} 领域模型
   */
  private toModel(row: SearchHistoryRow): SearchHistory {
    const history: SearchHistory = new SearchHistory();
    history.keyword = row.keyword ?? "";
    history.searchTime = Number(row.search_time ?? Date.now());
    return history;
  }
}
