import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { SettingsSectionItem } from './SettingsCommon';

export interface SettingsNavigationHeaderOptions {
  colors: ColorsInterface;
  title: string;
  onBack: () => void;
}

export interface SettingsNavigationMenuOptions {
  colors: ColorsInterface;
  items: SettingsSectionItem[];
  onSelect: (sectionId: string) => void;
}

class SettingsNavigationDataSource implements IDataSource {
  private items: SettingsSectionItem[];
  private listeners: DataChangeListener[] = [];

  constructor(items: SettingsSectionItem[]) {
    this.items = items;
  }

  totalCount(): number {
    return this.items.length;
  }

  getData(index: number): SettingsSectionItem {
    return this.items[index];
  }

  registerDataChangeListener(listener: DataChangeListener): void {
    if (this.listeners.indexOf(listener) < 0) this.listeners.push(listener);
  }

  unregisterDataChangeListener(listener: DataChangeListener): void {
    this.listeners = this.listeners.filter((item: DataChangeListener) => item !== listener);
  }
}

@Builder
export function SettingsNavigationHeader(options: SettingsNavigationHeaderOptions) {
  Row() {
    Text('←')
      .id('settings_back_button')
      .fontSize(DesignTokens.Typography.FONT_SIZE_2XL)
      .fontColor(options.colors.GRAY_900)
      .onClick(options.onBack)
    
    Text(options.title)
      .fontSize(DesignTokens.Typography.FONT_SIZE_XL)
      .fontWeight(DesignTokens.Typography.FONT_WEIGHT_BOLD)
      .fontColor(options.colors.GRAY_900)
      .margin({ left: DesignTokens.Spacing.LG })
    
    Blank()
  }
  .width('100%')
  .height(56)
  .padding({ left: DesignTokens.Layout.CONTAINER_PADDING, right: DesignTokens.Layout.CONTAINER_PADDING })
  .backgroundColor(options.colors.SURFACE_ELEVATED)
  .shadow({ color: options.colors.SHADOW_LIGHT, radius: 4, offsetX: 0, offsetY: 2 })
}

@Builder
export function SettingsNavigationMenu(options: SettingsNavigationMenuOptions) {
  List() {
    LazyForEach(new SettingsNavigationDataSource(options.items), (item: SettingsSectionItem) => {
      ListItem() {
        Column() {
          Row() {
            Column() {
              Text(item.title)
                .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
                .fontColor(options.colors.GRAY_900)
                .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
              Text(item.subtitle)
                .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
                .fontColor(options.colors.GRAY_600)
                .margin({ top: 4 })
            }
            .layoutWeight(1)
            Text('›').fontSize(DesignTokens.Typography.FONT_SIZE_LG).fontColor(options.colors.GRAY_400)
          }
          .width('100%')
          .height(64)
          .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
          .alignItems(VerticalAlign.Center)
          .id(item.id === 'sync' ? 'webdav_settings_entry' : '')
          .onClick(() => {
            options.onSelect(item.id);
          })

          Divider().color(options.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
        }
      }
      .height(65)
    }, (item: SettingsSectionItem) => item.id)
  }
  .width('100%')
  .height(options.items.length * 65)
  .cachedCount(2)
  .enableScrollInteraction(false)
  .scrollBar(BarState.Off)
  .backgroundColor(options.colors.SURFACE_PRIMARY)
  .borderRadius(DesignTokens.BorderRadius.LG)
  .shadow(DesignTokens.Shadows.CARD_ELEVATION_1)
  .margin({ top: DesignTokens.Spacing.LG })
}

export const SETTINGS_SECTIONS: SettingsSectionItem[] = [
  { id: 'preferences', title: '学习与偏好', subtitle: '任务计划、语音、难度与语境' },
  { id: 'dictionary', title: '外部词典', subtitle: '外链词典模板配置' },
  { id: 'fsrs', title: 'FSRS优化', subtitle: '根据记忆表现优化算法参数' },
  { id: 'api', title: 'API配置', subtitle: '提供商、接口与模型选择' },
  { id: 'sync', title: 'WebDAV 配置', subtitle: '云端连接与自动同步设置' },
  { id: 'backup', title: '备份与恢复', subtitle: '云端/本地数据导入导出' },
  { id: 'about', title: '关于', subtitle: '版本、隐私与开源信息' }
];

export function getSettingsSectionTitle(sectionId: string): string {
  if (sectionId.length === 0) {
    return '设置';
  }
  const item = SETTINGS_SECTIONS.find(s => s.id === sectionId);
  return item ? item.title : '设置';
}

