import { Table, Column, PrimaryKey, ColumnType } from "@ibestservices/ibest-orm";

/**
 * @file 搜索历史数据库实体，映射 goods_search_history 表。
 * @author Joker.X
 */
@Table({ name: "goods_search_history" })
export class SearchHistoryEntity {
  /**
   * 自增主键（ibest-orm 的 @PrimaryKey 固定为 INTEGER 类型，不能直接用文本关键词做主键）
   */
  @PrimaryKey()
  id?: number;
  /**
   * 搜索关键词，由数据源保证唯一
   */
  @Column({ type: ColumnType.TEXT })
  keyword?: string;
  /**
   * 搜索时间戳
   */
  @Column({ type: ColumnType.INTEGER })
  searchTime?: number;
}
