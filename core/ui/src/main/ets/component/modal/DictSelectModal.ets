import {
  ColumnStart, P100, SpaceVerticalLarge
} from "designsystem";
import { BaseNetWorkUiState } from "base";
import { DictItem } from "model";
import { IBestButton, IBestCell, IBestCellGroup, IBestCheckbox, IBestCheckboxGroup } from "ibestui";
import { BottomModal } from "./BottomModal";
import { BaseNetWorkView } from "../network/BaseNetWorkView";
import { EmptyNetwork } from "../empty/EmptyNetwork";
import { PageLoading } from "../loading/PageLoading";

/**
 * @file 字典选择弹窗组件
 * @author Joker.X
 */
@ComponentV2
export struct DictSelectModal {
  /**
   * 是否显示弹窗
   */
  @Param
  @Require
  visible: boolean = false;
  /**
   * 弹窗标题
   */
  @Param
  title: ResourceStr = $r("app.string.please_select");
  /**
   * 关闭回调
   */
  @Param
  onDismiss: () => void = () => {
  };
  /**
   * 网络请求状态
   */
  @Param
  uiState: BaseNetWorkUiState = BaseNetWorkUiState.LOADING;
  /**
   * 字典项列表数据
   */
  @Param
  dictList: DictItem[] = [];
  /**
   * 当前选中的字典项
   */
  @Param
  selectedItem: DictItem | null = null;
  /**
   * 字典项选择回调
   * @param {DictItem} item - 选中的字典项
   */
  @Param
  onItemSelected: (item: DictItem) => void = () => {
  };
  /**
   * 确认按钮回调
   * @param {DictItem | null} item - 当前选中的字典项
   */
  @Param
  onConfirm: (item: DictItem | null) => void = () => {
  };
  /**
   * 重试回调
   */
  @Param
  onRetry: () => void = () => {
  };
  /**
   * 复选框分组 ID（用于控制选中态）
   */
  @Local
  private readonly groupId: string = "dict_select_group";

  /**
   * 构建字典选择弹窗
   * @returns {void} 无返回值
   */
  build(): void {
    BottomModal({
      visible: this.visible,
      title: this.title,
      onDismiss: this.onDismiss,
      containerColor: $r("app.color.bg_grey"),
      content: (): void => this.ModalContentNetWorkLayout()
    });
  }

  /**
   * 弹窗内容包装器（包含网络状态处理）
   * @returns {void} 无返回值
   */
  @Builder
  private ModalContentNetWorkLayout(): void {
    BaseNetWorkView({
      uiState: this.uiState,
      onRetry: this.onRetry,
      loadingBuilder: (): void => this.CustomLoading(),
      errorBuilder: (): void => this.CustomError(),
      content: (): void => this.ModalContent()
    });
  }

  /**
   * 弹窗内容
   * @returns {void} 无返回值
   */
  @Builder
  private ModalContent(): void {
    ColumnStart({ widthValue: P100 }) {
      Scroll() {
        IBestCheckboxGroup({ group: this.groupId, activeList: this.getActiveList() }) {
          IBestCellGroup({
            inset: true,
            radius: $r("app.float.radius_medium"),
            outerMargin: 0
          }) {
            ForEach(this.dictList, (item: DictItem, index: number): void => {
              IBestCell({
                title: item.name ?? "",
                center: true,
                clickable: true,
                hasBorder: index !== this.dictList.length - 1,
                rightIconBuilder: (): void => this.DictItemCheckbox(this.getItemKey(item, index)),
                onCellClick: (): void => this.onItemClick(item)
              });
            }, (item: DictItem, index: number): string => `${item.id ?? 0}-${index}`);
          }
        }
      }
      .width(P100)
      .scrollBar(BarState.Off);

      SpaceVerticalLarge();

      IBestButton({
        text: $r("app.string.confirm"),
        type: "primary",
        round: true,
        btnWidth: P100,
        disabled: this.selectedItem === null,
        onBtnClick: (): void => this.handleConfirm()
      });
    }
  }

  /**
   * 字典项右侧选择器
   * @param {string} name - 选项名称
   * @returns {void} 无返回值
   */
  @Builder
  private DictItemCheckbox(name: string): void {
    IBestCheckbox({
      group: this.groupId,
      name: name
    });
  }

  /**
   * 处理字典项点击
   * @param {DictItem} item - 字典项
   * @returns {void} 无返回值
   */
  private onItemClick(item: DictItem): void {
    this.onItemSelected(item);
  }

  /**
   * 获取当前选中列表
   * @returns {string[]} 选中列表
   */
  private getActiveList(): string[] {
    if (!this.selectedItem) {
      return [];
    }
    return [this.getItemKey(this.selectedItem, 0)];
  }

  /**
   * 获取字典项 Key
   * @param {DictItem} item - 字典项
   * @param {number} index - 下标
   * @returns {string} Key
   */
  private getItemKey(item: DictItem, index: number): string {
    const itemId: number | null | undefined = item.id;
    if (itemId === null || itemId === undefined) {
      return `${index}`;
    }
    return `${itemId}`;
  }

  /**
   * 处理确认按钮点击
   * @returns {void} 无返回值
   */
  private handleConfirm(): void {
    this.onConfirm(this.selectedItem);
    this.onDismiss();
  }

  /**
   * 自定义加载状态
   * @returns {void} 无返回值
   */
  @Builder
  private CustomLoading(): void {
    Column() {
      PageLoading();
    }
    .height(300)
    .width(P100);
  }

  /**
   * 自定义错误状态
   * @returns {void} 无返回值
   */
  @Builder
  private CustomError(): void {
    Column() {
      EmptyNetwork({
        onAction: (): void => this.onRetry()
      });
    }
    .height(300)
    .width(P100);
  }
}
