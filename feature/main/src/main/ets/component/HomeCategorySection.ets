import { P100, SpaceVerticalXSmall } from "designsystem";
import { Category } from "model";
import { bp } from "state";
import { Card, NetWorkImage } from "ui";

/**
 * @file 首页分类卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct HomeCategorySection {
  /**
   * 分类列表
   */
  @Param
  categories: Category[] = [];
  /**
   * 分类点击回调
   */
  @Param
  onCategoryClick: (id: number) => void = () => {
  };

  /**
   * 构建分类卡片
   * @returns {void} 无返回值
   */
  build(): void {
    if (this.categories && this.categories.length > 0) {
      Card({ paddingValue: $r("app.float.space_padding_small") }) {
        Grid() {
          ForEach(this.categories, (category: Category): void => {
            GridItem() {
              this.categoryItem(category);
            }
          }, (category: Category): string => `${category.id}-${category.name}`);
        }
        .columnsTemplate(this.buildColumnsTemplate())
        .columnsGap($r("app.float.space_horizontal_small_x"))
        .rowsGap($r("app.float.space_vertical_small_x"))
        .width(P100);
      }
    }
  }

  /**
   * 分类项视图
   * @param {Category} category - 分类数据
   * @returns {void} 无返回值
   */
  @Builder
  private categoryItem(category: Category): void {
    Column() {
      NetWorkImage({
        model: category.pic ?? null,
        sizeValue: this.getImageSize(),
        cornerRadius: this.getImageRadius(),
        showBackground: true,
        backgroundColorValue: $r("app.color.bg_grey")
      });

      SpaceVerticalXSmall();

      Text(category.name)
        .fontSize($r("app.float.headline_medium"))
        .fontColor($r("app.color.text_primary"))
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis });
    }
    .width(P100)
    .padding({
      top: $r("app.float.space_vertical_small_x"),
      bottom: $r("app.float.space_vertical_small_x")
    })
    .alignItems(HorizontalAlign.Center)
    .onClick((): void => this.onCategoryClick(category.id));
  }

  /**
   * 获取列数模板
   * @returns {string} Grid 列模板
   */
  private buildColumnsTemplate(): string {
    const columns: number = this.getColumnsCount();
    let template: string = "";
    for (let index: number = 0; index < columns; index++) {
      template = `${template}1fr${index === columns - 1 ? "" : " "}`;
    }
    return template;
  }

  /**
   * 获取当前断点对应的列数
   * @returns {number} 列数
   */
  private getColumnsCount(): number {
    return bp({ sm: 5, md: 10, lg: 10 });
  }

  /**
   * 获取分类图标尺寸
   * @returns {number} 图标尺寸
   */
  private getImageSize(): number {
    return bp({ sm: 48, md: 56, lg: 60 });
  }

  /**
   * 获取分类图标圆角
   * @returns {number} 图标圆角
   */
  private getImageRadius(): number {
    const size: number = this.getImageSize();
    return size / 2;
  }
}
