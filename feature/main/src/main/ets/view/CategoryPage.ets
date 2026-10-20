import { AppNavDestination } from 'ui';
import CategoryViewModel from '../viewmodel/CategoryViewModel';

@ComponentV2
export struct CategoryPage {
  @Local private vm: CategoryViewModel = new CategoryViewModel();
  @Param embedded: boolean = false;
  private categories: string[] = ['家居生活', '厨房餐具', '数码好物', '出行随身', '灯具照明', '收纳整理'];

  @Builder
  private CategoryContent() {
    Column({ space: 24 }) {
      Text('分类').fontSize(26).fontWeight(FontWeight.Bold).fontColor('#222222').width('100%')
      Text('按生活场景，发现所需好物').fontSize(14).fontColor('#888888').width('100%')
      ForEach(this.categories, (name: string) => {
        Row() {
          Text(name).fontSize(17).fontColor('#333333')
          Blank()
          Text('精选').fontSize(12).fontColor('#8A948E')
        }.width('100%').padding(22).backgroundColor('#FFFFFF').borderRadius(16)
      }, (name: string): string => name)
    }.id('category_page').width('100%').height('100%').padding(22)
    .alignItems(HorizontalAlign.Start).backgroundColor('#F6F7F8')
  }

  build() {
    if (this.embedded) { this.CategoryContent(); } else {
      AppNavDestination({ title: '分类', viewModel: this.vm }) { this.CategoryContent(); }
    }
  }
}
