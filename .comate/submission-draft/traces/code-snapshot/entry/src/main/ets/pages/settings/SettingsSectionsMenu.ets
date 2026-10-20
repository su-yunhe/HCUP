import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { SettingsSectionItem } from './SettingsCommon';

export const SETTINGS_SECTIONS: SettingsSectionItem[] = [
  { id: 'preferences', title: '学习与偏好', subtitle: '任务计划、语音、难度与语境' },
  { id: 'dictionary', title: '外部词典', subtitle: '外链词典模板配置' },
  { id: 'fsrs', title: 'FSRS优化', subtitle: '根据记忆表现优化算法参数' },
  { id: 'api', title: 'API配置', subtitle: '提供商、接口与模型选择' },
  { id: 'sync', title: 'WebDAV 配置', subtitle: '云端连接与自动同步设置' },
  { id: 'backup', title: '备份与恢复', subtitle: '云端/本地数据导入导出' },
  { id: 'logger', title: '日志与调试', subtitle: '查看、导出与持久化策略（默认 WARN/ERROR）' },
  { id: 'about', title: '关于', subtitle: '版本、隐私与开源信息' }
];

class SettingsSectionsDataSource implements IDataSource {
  private listener: DataChangeListener | null = null;

  totalCount(): number {
    return SETTINGS_SECTIONS.length;
  }

  getData(index: number): SettingsSectionItem {
    return SETTINGS_SECTIONS[index];
  }

  registerDataChangeListener(listener: DataChangeListener): void {
    this.listener = listener;
  }

  unregisterDataChangeListener(listener: DataChangeListener): void {
    if (this.listener === listener) this.listener = null;
  }
}

@Component
export struct SettingsSectionsMenu {
  @Prop colors: ColorsInterface = ThemeManager.getInstance().getColors();
  onSelect: (id: string) => void = () => {};
  private dataSource: SettingsSectionsDataSource = new SettingsSectionsDataSource();

  build() {
    List() {
      LazyForEach(this.dataSource, (item: SettingsSectionItem) => {
        ListItem() {
          Column() {
            Row() {
              Column() {
                Text(item.title)
                  .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
                  .fontColor(this.colors.GRAY_900)
                  .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
                Text(item.subtitle)
                  .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
                  .fontColor(this.colors.GRAY_600)
                  .margin({ top: 4 })
              }
              .layoutWeight(1)
              Text('›').fontSize(DesignTokens.Typography.FONT_SIZE_LG).fontColor(this.colors.GRAY_400)
            }
            .id('settings_section_' + item.id)
            .width('100%')
            .height(64)
            .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
            .alignItems(VerticalAlign.Center)
            .onClick(() => this.onSelect(item.id))

            Divider().height(1).color(this.colors.GRAY_200)
              .margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
          }
        }
      }, (item: SettingsSectionItem) => item.id)
    }
    .width('100%')
    .height(SETTINGS_SECTIONS.length * 65)
    .cachedCount(2)
    .enableScrollInteraction(false)
    .scrollBar(BarState.Off)
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
    .shadow(DesignTokens.Shadows.CARD_ELEVATION_1)
    .margin({ top: DesignTokens.Spacing.LG })
  }
}
