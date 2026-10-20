/**
 * @file 商品详情图片懒加载数据源
 */
export class GoodsDetailImageDataSource implements IDataSource {
  /**
   * 图片地址列表
   */
  private images: string[] = [];
  /**
   * 数据变化监听器
   */
  private listeners: DataChangeListener[] = [];

  /**
   * 替换全部图片并通知刷新
   * @param {string[]} images - 图片地址列表
   * @returns {void} 无返回值
   */
  setData(images: string[]): void {
    this.images = images;
    this.listeners.forEach((listener: DataChangeListener): void => listener.onDataReloaded());
  }

  totalCount(): number {
    return this.images.length;
  }

  getData(index: number): string {
    return this.images[index];
  }

  registerDataChangeListener(listener: DataChangeListener): void {
    if (this.listeners.indexOf(listener) < 0) {
      this.listeners.push(listener);
    }
  }

  unregisterDataChangeListener(listener: DataChangeListener): void {
    const index: number = this.listeners.indexOf(listener);
    if (index >= 0) {
      this.listeners.splice(index, 1);
    }
  }
}
