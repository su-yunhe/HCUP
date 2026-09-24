import { SelectedGoods } from "../entity/SelectedGoods";

/**
 * @file 创建订单请求模型
 * @author Joker.X
 */

/**
 * 创建订单请求初始化参数
 */
interface CreateOrderRequestInit {
  /**
   * 创建订单所需参数
   */
  data: CreateOrderInit;
}

/**
 * 创建订单初始化参数
 */
interface CreateOrderInit {
  /**
   * 备注信息
   */
  remark?: string;
  /**
   * 地址ID
   */
  addressId: number;
  /**
   * 选中的商品列表
   */
  goodsList: SelectedGoods[];
  /**
   * 优惠券ID（可选）
   */
  couponId?: number | null;
  /**
   * 标题
   */
  title?: string;
}

export class CreateOrderRequest {
  /**
   * 创建订单所需参数
   */
  data: CreateOrder;

  /**
   * @param {CreateOrderRequestInit} init - 初始化数据
   */
  constructor(init: CreateOrderRequestInit) {
    this.data = new CreateOrder(init.data);
  }
}

/**
 * 创建订单所需参数
 */
export class CreateOrder {
  /**
   * 备注信息
   */
  remark?: string;
  /**
   * 地址ID
   */
  addressId: number;
  /**
   * 选中的商品列表
   */
  goodsList: SelectedGoods[];
  /**
   * 优惠券ID（可选）
   */
  couponId?: number | null;
  /**
   * 标题
   */
  title?: string;

  /**
   * @param {CreateOrderInit} init - 初始化数据
   */
  constructor(init: CreateOrderInit) {
    this.addressId = init.addressId;
    this.goodsList = init.goodsList.map((g) => new SelectedGoods(g));
    if (init.remark !== undefined) {
      this.remark = init.remark;
    }
    if (init.couponId !== undefined) {
      this.couponId = init.couponId;
    }
    if (init.title !== undefined) {
      this.title = init.title;
    }
  }
}
