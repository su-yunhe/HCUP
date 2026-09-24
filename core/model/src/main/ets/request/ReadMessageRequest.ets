/**
 * @file 已读消息请求模型
 * @author Joker.X
 */
export class ReadMessageRequest {
  /**
   * 消息ID数组，用于批量已读
   */
  ids: number[];

  /**
   * @param {ReadMessageRequest} init - 初始化数据
   */
  constructor(init: ReadMessageRequest) {
    this.ids = init.ids;
  }
}
