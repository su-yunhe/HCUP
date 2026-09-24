/**
 * @file 字典数据请求
 * @author Joker.X
 */
export class DictDataRequest {
  /**
   * 字典类型列表
   */
  types: string[];

  /**
   * @param {DictDataRequest} init - 初始化数据
   */
  constructor(init: DictDataRequest) {
    this.types = init.types;
  }
}
