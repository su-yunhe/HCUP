from pathlib import Path

root = Path('D:/HCUP/vg-spec13/entry/src/main/ets/pages')
page = root / 'SettingsPage.ets'
source = page.read_text(encoding='utf-8')
header_start = source.index('        // Header\n')
header_end = source.index('        Scroll() {', header_start)
header = source[header_start:header_end]
header = '\n'.join(line[8:] if line.startswith('        ') else line for line in header.splitlines())
header = header.replace('// Header\n', '').replace('this.colors', 'options.colors').replace('this.getActiveSectionTitle()', 'options.title').replace('() => { this.handleHeaderBack(); }', 'options.onBack')
menu_start = source.index('              Column() {', header_end)
menu_end = source.index('            } else {', menu_start)
menu = source[menu_start:menu_end]
menu = '\n'.join(line[14:] if line.startswith('              ') else line for line in menu.splitlines())
menu = menu.replace('this.colors', 'options.colors').replace('SETTINGS_SECTIONS', 'options.items').replace('this.activeSectionId = item.id;', 'options.onSelect(item.id);')
source = source[:menu_start] + '''              SettingsNavigationMenu({
                colors: this.colors, items: SETTINGS_SECTIONS,
                onSelect: (sectionId: string): void => { this.activeSectionId = sectionId; }
              })
''' + source[menu_end:]
source = source[:header_start] + '''        SettingsNavigationHeader({
          colors: this.colors, title: this.getActiveSectionTitle(),
          onBack: (): void => { this.handleHeaderBack(); }
        })

''' + source[header_end:]
source = source.replace("import { SettingsSectionItem } from './settings/SettingsCommon';", "import { SettingsSectionItem } from './settings/SettingsCommon';\nimport { SettingsNavigationHeader, SettingsNavigationMenu } from './settings/SettingsNavigationBuilders';")
constants_start = source.index('const SETTINGS_SECTIONS:')
constants_end = source.index('interface LearningOrderPolicyJson', constants_start)
constants = source[constants_start:constants_end].replace('const SETTINGS_SECTIONS:', 'export const SETTINGS_SECTIONS:')
source = source[:constants_start] + source[constants_end:]
title_start = source.index('  private getActiveSectionTitle(): string {')
title_end = source.index('  private loadWebDavSettings()', title_start)
title = source[title_start:title_end]
title = '\n'.join(line[2:] if line.startswith('  ') else line for line in title.splitlines())
title = title.replace('private getActiveSectionTitle(): string', 'export function getSettingsSectionTitle(sectionId: string): string').replace('this.activeSectionId', 'sectionId')
source = source[:title_start] + source[title_end:]
source = source.replace('this.getActiveSectionTitle()', 'getSettingsSectionTitle(this.activeSectionId)')
source = source.replace("import { SettingsSectionItem } from './settings/SettingsCommon';\n", '')
source = source.replace('SettingsNavigationHeader, SettingsNavigationMenu }', 'SettingsNavigationHeader, SettingsNavigationMenu, SETTINGS_SECTIONS, getSettingsSectionTitle }')
source = source[source.index("import router"):]
builders = '''import { DesignTokens } from '../../model/DesignTokens';
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

@Builder
export function SettingsNavigationHeader(options: SettingsNavigationHeaderOptions) {
''' + '\n'.join('  ' + line if line else '' for line in header.splitlines()) + '''
}

@Builder
export function SettingsNavigationMenu(options: SettingsNavigationMenuOptions) {
''' + '\n'.join('  ' + line if line else '' for line in menu.splitlines()) + '''
}
'''
builders += '\n' + constants + title + '\n'
assert 'this.' not in builders
assert len(source.splitlines()) <= 500, len(source.splitlines())
(root / 'settings/SettingsNavigationBuilders.ets').write_text(builders, encoding='utf-8')
page.write_text(source, encoding='utf-8')
print('SettingsPage:', len(source.splitlines()), 'lines; navigation builders:', len(builders.splitlines()), 'lines')
