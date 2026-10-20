import { SelectedGoods } from "../entity/SelectedGoods";

/** Explicit data-only initializers allow typed literals with ArkTS's nominal class rules. */
export interface CreateOrderInit {
  remark?: string;
  addressId: number;
  goodsList: SelectedGoods[];
  couponId?: number | null;
  title?: string;
}

export interface CreateOrderRequestInit {
  data: CreateOrderInit;
}

/**
 * @file 创建订单请求模型
 * @author Joker.X
 */
export class CreateOrderRequest implements CreateOrderRequestInit {
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
export class CreateOrder implements CreateOrderInit {
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
