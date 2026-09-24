/**
 * @file 提交意见反馈请求模型
 * @author Joker.X
 */
export class FeedbackSubmitRequest {
  /**
   * 联系方式
   */
  contact?: string | null;
  /**
   * 类型
   */
  type: number;
  /**
   * 内容
   */
  content: string;
  /**
   * 图片
   */
  images?: string[] | null;

  /**
   * @param {FeedbackSubmitRequest} init - 初始化数据
   */
  constructor(init: FeedbackSubmitRequest) {
    this.type = init.type;
    this.content = init.content;
    if (init.contact !== undefined) {
      this.contact = init.contact;
    }
    if (init.images !== undefined) {
      this.images = init.images;
    }
  }
}
