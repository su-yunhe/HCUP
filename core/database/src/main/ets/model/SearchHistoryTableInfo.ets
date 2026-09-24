/**
 * @file 搜索历史表结构信息
 * @author Joker.X
 */
export interface SearchHistoryTableInfo {
  /**
   * 列名
   */
  name: string;
  /**
   * 列类型
   */
  type: string;
  /**
   * 是否不能为空
   */
  notnull: boolean;
  /**
   * 是否主键
   */
  pk: boolean;
}
