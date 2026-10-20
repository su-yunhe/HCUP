import { BaseViewModel } from 'base';

export class HomeProduct {
  id: string;
  name: string;
  detail: string;
  price: string;
  picture: string;
  constructor(id: string, name: string, detail: string, price: string, picture: string) {
    this.id = id;
    this.name = name;
    this.detail = detail;
    this.price = price;
    this.picture = picture;
  }
}

@ObservedV2
export default class HomeViewModel extends BaseViewModel {
  readonly products: HomeProduct[] = [
    new HomeProduct('mug', '陶瓷马克杯', '温润釉面 · 让每一杯都温暖', '39', 'mug'),
    new HomeProduct('lamp', '柔光阅读灯', '三档暖光 · 陪伴专注时光', '129', 'lamp'),
    new HomeProduct('vase', '素色花器', '简约线条 · 给生活一点自然', '59', 'vase'),
    new HomeProduct('bag', '日常帆布袋', '轻便耐用 · 装下出门好心情', '49', 'bag'),
    new HomeProduct('kettle', '手冲分享壶', '细嘴控水 · 慢慢享受咖啡香', '89', 'kettle'),
    new HomeProduct('speaker', '桌面蓝牙音箱', '小巧随行 · 留住喜欢的旋律', '169', 'speaker'),
    new HomeProduct('mug-set', '双人杯组合', '午后茶歇 · 与朋友分享片刻', '69', 'mug'),
    new HomeProduct('bedside', '床头氛围灯', '柔和不刺眼 · 为夜晚留一盏灯', '99', 'lamp')
  ];
}
