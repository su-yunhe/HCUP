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
  { id: 'about', title: '关于', subtitle: '版本、隐私与开源信息' }
];

// The seven settings entries are immutable; no change notifications are needed.
class SettingsSectionDataSource implements IDataSource {
  totalCount(): number {
    return SETTINGS_SECTIONS.length;
  }

  getData(index: number): SettingsSectionItem {
    return SETTINGS_SECTIONS[index];
  }

  registerDataChangeListener(_listener: DataChangeListener): void {}

  unregisterDataChangeListener(_listener: DataChangeListener): void {}
}

@Component
export struct SettingsOverviewSection {
  @Prop colors: ColorsInterface = ThemeManager.getInstance().getColors();
  onSelect: (sectionId: string) => void = () => {};
  private entries: SettingsSectionDataSource = new SettingsSectionDataSource();

  build() {
    List() {
      LazyForEach(this.entries, (item: SettingsSectionItem) => {
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
            .id(item.id === 'sync' ? 'settings_webdav_entry' : 'settings_entry_' + item.id)
            .width('100%')
            .height(64)
            .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
            .alignItems(VerticalAlign.Center)
            .onClick(() => { this.onSelect(item.id); })
            Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
          }
          .width('100%')
        }
      }, (item: SettingsSectionItem) => item.id)
    }
    .width('100%')
    .height(SETTINGS_SECTIONS.length * 65)
    .cachedCount(SETTINGS_SECTIONS.length)
    .enableScrollInteraction(false)
    .scrollBar(BarState.Off)
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
    .shadow(DesignTokens.Shadows.CARD_ELEVATION_1)
    .margin({ top: DesignTokens.Spacing.LG })
  }
}
