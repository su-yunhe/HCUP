import { IBestNavBar, IBestSearch } from "ibestui";
import { P100 } from "designsystem";
import { ArrowLeftIcon } from "../icon/ArrowLeftIcon";

/**
 * @file 搜索顶部栏组件
 * @author Joker.X
 */
@ComponentV2
export struct SearchTopAppBar {
  /**
   * 搜索输入值
   */
  @Param
  value: string = "";
  /**
   * 占位文案
   */
  @Param
  placeholder: ResourceStr = $r("app.string.search_hint");
  /**
   * 是否自动聚焦
   */
  @Param
  autoFocus: boolean = false;
  /**
   * 是否只读
   */
  @Param
  readOnly: boolean = false;
  /**
   * 输入值变化回调
   */
  @Param
  onValueChange: (value: string) => void = () => {
  };
  /**
   * 输入框聚焦回调
   */
  @Param
  onInputFocus: () => void = () => {
  };
  /**
   * 搜索回调
   */
  @Param
  onSearch: (value: string) => void = () => {
  };
  /**
   * 返回按钮点击回调
   */
  @Param
  onBackClick: () => void = () => {
  };
  /**
   * 是否显示右侧区域
   */
  @Param
  isShowRight: boolean = false;
  /**
   * 右侧自定义区域
   */
  @BuilderParam
  rightBuilder: CustomBuilder;

  /**
   * 构建搜索顶部栏
   * @returns {void} 无返回值
   */
  build(): void {
    IBestNavBar({
      isShowBorder: false,
      leftRightPadding: 12,
      navBarBgColor: $r("app.color.bg_grey"),
      leftBuilder: (): void => this.buildLeft(),
      titleBuilder: (): void => this.buildTitle(),
      isShowRight: this.isShowRight && this.rightBuilder !== undefined,
      rightBuilder: (): void => this.buildRight()
    });
  }

  /**
   * 左侧返回按钮
   * @returns {void} 无返回值
   */
  @Builder
  private buildLeft(): void {
    ArrowLeftIcon({
      iconSize: 24,
      onTap: (): void => this.onBackClick()
    });
  }

  /**
   * 标题区域（搜索框）
   * @returns {void} 无返回值
   */
  @Builder
  private buildTitle(): void {
    IBestSearch({
      value: this.value,
      placeholder: this.placeholder,
      autoFocus: this.autoFocus,
      readOnly: this.readOnly,
      isRound: true,
      clearable: true,
      outBgColor: $r("app.color.bg_grey"),
      innerBgColor: $r("app.color.bg_white"),
      placeholderColor: $r("app.color.text_tertiary"),
      textColor: $r("app.color.text_primary"),
      customRightButton: (): void => this.buildSearchButton(),
      onInput: (value: string): void => this.onValueChange(value),
      onInputFocus: (): void => this.onInputFocus(),
      onSearch: (): void => this.handleSearch(),
      onClear: (): void => this.onValueChange("")
    })
    .width(P100);
  }

  /**
   * 右侧自定义区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildRight(): void {
    if (this.rightBuilder) {
      this.rightBuilder();
    }
  }

  /**
   * 右侧搜索按钮
   * @returns {void} 无返回值
   */
  @Builder
  private buildSearchButton(): void {
    Text($r("app.string.search"))
      .fontColor($r("app.color.text_primary"))
      .fontSize($r("app.float.body_medium"))
      .padding({ left: 10, right: 10 })
      .onClick((): void => this.handleSearch());
  }

  /**
   * 触发搜索
   * @returns {void} 无返回值
   */
  private handleSearch(): void {
    this.onSearch(this.value);
  }
}
