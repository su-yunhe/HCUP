/**
 * @file 搜索历史表行结构
 * @author Joker.X
 */
export interface SearchHistoryRow {
  /**
   * 搜索关键词
   */
  keyword?: string;
  /**
   * 搜索时间戳（数据库列名）
   */
  search_time?: number;
}

