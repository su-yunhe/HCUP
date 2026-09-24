import { ColumnStart, P100, RowStartTop, SpaceVerticalSmall, SpaceVerticalXSmall } from "designsystem";
import { CategoryTree } from "model";
import { bp, getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { AppNavDestination, BaseNetWorkView, IBestSideBar, IBestSideBarItem, NetWorkImage, TitleWithLine } from "ui";
import CategoryViewModel from "../viewmodel/CategoryViewModel";

/**
 * @file 分类页面视图
 * @author Joker.X
 */
@ComponentV2
export struct CategoryPage {
  /**
   * 分类页面 ViewModel
   */
  @Local
  private vm: CategoryViewModel = new CategoryViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();
  /**
   * 右侧列表滚动控制器
   */
  private rightListScroller: Scroller = new Scroller();
  /**
   * 侧边栏分组 ID
   */
  private sideBarGroupId: string = "category-side-bar";

  /**
   * 构建分类页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.category"),
      viewModel: this.vm,
      pageBackgroundColor: $r("app.color.bg_white"),
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      },
      titleOptions: {
        backgroundColor: $r("app.color.bg_white")
      }
    }) {
      BaseNetWorkView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.CategoryContent()
      })
    }
  }

  /**
   * 分类页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private CategoryContent(): void {
    RowStartTop({ fillMaxSize: true }) {
      if (this.vm.categoryTitles.length > 0) {
        Column() {
          IBestSideBar({
            groupId: this.sideBarGroupId,
            active: this.vm.getActiveIndex(),
            activeFontColor: $r("app.color.primary"),
            bgColor: $r("app.color.bg_grey"),
            activeBgColor: $r("app.color.bg_white"),
            sideWidth: bp({ sm: 80, md: 100, lg: 120 }),
            onChange: (index: number): void => this.onSideBarChange(index)
          }) {
            ForEach(this.vm.categoryTitles, (item: string, index: number): void => {
              IBestSideBarItem({
                groupId: this.sideBarGroupId,
                index: index,
                title: item,
                contentPadding: {
                  top: $r("app.float.space_vertical_large"),
                  bottom: $r("app.float.space_vertical_large")
                }
              });
              SpaceVerticalSmall()
            }, (item: string, index: number): string => `${index}-${item}`);
          }
        }
        .height(P100)
        .backgroundColor($r("app.color.bg_grey"))
      }

      Column() {
        List({
          space: 12,
          scroller: this.rightListScroller
        }) {
          ForEach(this.vm.categoryTrees, (item: CategoryTree, index: number): void => {
            ListItem() {
              this.buildCategorySection(item);
            };
          }, (item: CategoryTree): string => `${item.id}`);
        }
        .padding({
          left: $r("app.float.space_padding_small"),
          right: $r("app.float.space_padding_small"),
          top: $r("app.float.space_padding_small")
        })
        .onScrollIndex((startIndex: number): void => {
          this.onRightListScroll(startIndex);
        })
        .width(P100);
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1)
      .height(P100)
      .backgroundColor($r("app.color.bg_white"));
    }
  }

  /**
   * 构建右侧分类分区
   * @param {CategoryTree} categoryTree - 分类树节点
   * @returns {void} 无返回值
   */
  @Builder
  private buildCategorySection(categoryTree: CategoryTree): void {
    ColumnStart({
      widthValue: P100,
      paddingValue: {
        bottom: $r("app.float.space_padding_large")
      }
    }) {
      TitleWithLine({ text: categoryTree.name });
      SpaceVerticalSmall();
      if (categoryTree.children.length > 0) {
        this.buildCategoryGrid(categoryTree.children);
      }
    };
  }

  /**
   * 构建分类网格
   * @param {CategoryTree[]} children - 子分类列表
   * @returns {void} 无返回值
   */
  @Builder
  private buildCategoryGrid(children: CategoryTree[]): void {
    Grid() {
      ForEach(children, (item: CategoryTree): void => {
        GridItem() {
          this.buildCategoryItem(item);
        };
      }, (item: CategoryTree): string => `${item.id}-${item.name}`);
    }
    .columnsTemplate(this.getCategoryColumnsTemplate())
    .columnsGap($r("app.float.space_padding_small"))
    .rowsGap($r("app.float.space_padding_small"))
    .width(P100);
  }

  /**
   * 构建分类项
   * @param {CategoryTree} category - 分类数据
   * @returns {void} 无返回值
   */
  @Builder
  private buildCategoryItem(category: CategoryTree): void {
    Column() {
      NetWorkImage({
        model: category.pic ?? null,
        sizeValue: bp({ sm: 56, md: 64, lg: 72 }),
        showBackground: false,
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
    .alignItems(HorizontalAlign.Center);
  }

  /**
   * 侧边栏切换事件
   * @param {number} index - 选中的索引
   * @returns {void} 无返回值
   */
  private onSideBarChange(index: number): void {
    const targetIndex: number = this.vm.onSideBarSelected(index);
    this.rightListScroller.scrollToIndex(targetIndex, true);
  }

  /**
   * 右侧列表滚动同步左侧选中
   * @param {number} startIndex - 当前可见起始索引
   * @returns {void} 无返回值
   */
  private onRightListScroll(startIndex: number): void {
    this.vm.onRightListScroll(startIndex);
  }

  /**
   * 获取分类网格列模板
   * @returns {string} 列模板字符串
   */
  private getCategoryColumnsTemplate(): string {
    const columnsCount: number = bp({ sm: 3, md: 4, lg: 6 });
    let template: string = "";
    for (let index: number = 0; index < columnsCount; index++) {
      template = `${template}1fr${index === columnsCount - 1 ? "" : " "}`;
    }
    return template;
  }
}
