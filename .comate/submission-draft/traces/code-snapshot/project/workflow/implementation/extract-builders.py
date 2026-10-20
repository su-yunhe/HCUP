from pathlib import Path
import re

root = Path('D:/HCUP/vg-spec13')
section_path = root / 'entry/src/main/ets/pages/settings/SettingsSyncSection.ets'
source = section_path.read_text(encoding='utf-8')
start = source.index('  @Builder\n  private buildInputField')
end = source.index('  build() {', start)
builders = source[start:end]

def extract(name, next_name):
    begin = builders.index('  @Builder\n  private ' + name)
    finish = builders.index('  @Builder\n  private ' + next_name) if next_name else len(builders)
    text = builders[begin:finish]
    return '\n'.join(line[2:] if line.startswith('  ') else line for line in text.splitlines()) + '\n'

input_field = extract('buildInputField', 'buildPasswordField').replace(
    'private buildInputField(label:',
    'function WebDavInputField(colors: ColorsInterface, disabled: boolean, inputId: string, label:')
input_field = input_field.replace('this.colors', 'colors').replace(
    '    .onChange(onChange)', '    .id(inputId)\n    .enabled(!disabled)\n    .onChange(onChange)')
password_field = extract('buildPasswordField', 'buildToggleRow').replace(
    'private buildPasswordField(label:',
    'function WebDavPasswordField(colors: ColorsInterface, disabled: boolean, inputId: string, label:')
password_field = password_field.replace('this.colors', 'colors').replace(
    '      .onChange(onChange)', '      .id(inputId)\n      .enabled(!disabled)\n      .onChange(onChange)').replace(
    '      .onClick(onToggle)', '      .enabled(!disabled)\n      .onClick(onToggle)')
toggle_row = extract('buildToggleRow', 'buildBasicConfigCard').replace(
    'private buildToggleRow(title:', 'function WebDavToggleRow(colors: ColorsInterface, title:').replace('this.colors', 'colors')

config = extract('buildBasicConfigCard', 'buildAutoSyncCard').replace(
    'private buildBasicConfigCard()', 'export function WebDavBasicConfigCard(options: WebDavConfigOptions)').replace('this.colors', 'options.colors')
config = config.replace("this.buildInputField('WebDAV 地址', this.webdavEndpoint, 'https://dav.example.com/dav/', (v) => this.webdavEndpoint = v)",
    "WebDavInputField(options.colors, options.disabled, 'webdav_endpoint_input', 'WebDAV 地址', options.endpoint, 'https://dav.example.com/dav/', options.onEndpointChange)")
config = config.replace("this.buildInputField('账号', this.webdavUsername, 'username', (v) => this.webdavUsername = v)",
    "WebDavInputField(options.colors, options.disabled, 'webdav_username_input', '账号', options.username, 'username', options.onUsernameChange)")
config = config.replace("this.buildPasswordField('密码', this.webdavPassword, 'password', this.showWebdavPassword, (v) => this.webdavPassword = v, () => this.showWebdavPassword = !this.showWebdavPassword)",
    "WebDavPasswordField(options.colors, options.disabled, 'webdav_password_input', '密码', options.password, 'password', options.showPassword, options.onPasswordChange, options.onTogglePassword)")
config = config.replace("this.buildPasswordField('同步密码（用于 AES 加密）', this.webdavSyncPassword, 'sync password', this.showWebdavSyncPassword, (v) => this.webdavSyncPassword = v, () => this.showWebdavSyncPassword = !this.showWebdavSyncPassword)",
    "WebDavPasswordField(options.colors, options.disabled, 'webdav_sync_password_input', '同步密码（用于 AES 加密）', options.syncPassword, 'sync password', options.showSyncPassword, options.onSyncPasswordChange, options.onToggleSyncPassword)")
config = config.replace("this.buildInputField('远端目录', this.webdavRemoteRoot, '/weiyu_sync', (v) => this.webdavRemoteRoot = v)",
    "WebDavInputField(options.colors, options.disabled, 'webdav_remote_root_input', '远端目录', options.remoteRoot, '/weiyu_sync', options.onRemoteRootChange)")

auto = extract('buildAutoSyncCard', 'buildActionButtonsCard').replace(
    'private buildAutoSyncCard()', 'export function WebDavAutoSyncCard(options: WebDavAutoSyncOptions)').replace('this.colors', 'options.colors')
auto = auto.replace("this.buildToggleRow('启用自动同步', '进入前台时按间隔自动同步', this.webdavAutoSyncEnabled, (isOn) => {\n      this.webdavAutoSyncEnabled = isOn;\n      this.saveWebDavAutoSyncSettings();\n    })",
    "WebDavToggleRow(options.colors, '启用自动同步', '进入前台时按间隔自动同步', options.enabled, options.onEnabledChange)")
auto = auto.replace("this.buildToggleRow('自动上传模型', '用于多端算法同步', this.webdavAutoSyncUploadModelEnabled, (isOn) => {\n        this.webdavAutoSyncUploadModelEnabled = isOn;\n        this.saveWebDavAutoSyncSettings();\n      })",
    "WebDavToggleRow(options.colors, '自动上传模型', '用于多端算法同步', options.uploadModel, options.onUploadModelChange)")
auto = auto.replace("this.buildToggleRow('自动上传全量备份', '只上传，不自动恢复覆盖本地', this.webdavAutoSyncUploadBackupEnabled, (isOn) => {\n        this.webdavAutoSyncUploadBackupEnabled = isOn;\n        this.saveWebDavAutoSyncSettings();\n      })",
    "WebDavToggleRow(options.colors, '自动上传全量备份', '只上传，不自动恢复覆盖本地', options.uploadBackup, options.onUploadBackupChange)")
auto = re.sub(r"this\.buildToggleRow\('启用自动同步'.*?\}\)", "WebDavToggleRow(options.colors, '启用自动同步', '进入前台时按间隔自动同步', options.enabled, options.onEnabledChange)", auto, flags=re.S)
auto = re.sub(r"this\.buildToggleRow\('自动上传模型'.*?\}\)", "WebDavToggleRow(options.colors, '自动上传模型', '用于多端算法同步', options.uploadModel, options.onUploadModelChange)", auto, flags=re.S)
auto = re.sub(r"this\.buildToggleRow\('自动上传全量备份'.*?\}\)", "WebDavToggleRow(options.colors, '自动上传全量备份', '只上传，不自动恢复覆盖本地', options.uploadBackup, options.onUploadBackupChange)", auto, flags=re.S)
auto = auto.replace('this.webdavAutoSyncEnabled', 'options.enabled').replace('this.webdavAutoSyncIntervalIndex', 'options.intervalIndex')
auto = auto.replace('.onSelect((index: number) => {\n          options.intervalIndex = index;\n          this.saveWebDavAutoSyncSettings();\n        })', '.onSelect(options.onIntervalChange)')
auto = auto.replace('this.formatWebDavAutoSyncLastSuccess()', 'options.lastSuccessText').replace('this.webdavAutoSyncLastError', 'options.lastError')
auto = re.sub(r'\.onSelect\(\(index: number\) => \{.*?\}\)', '.onSelect(options.onIntervalChange)', auto, flags=re.S)

actions = extract('buildActionButtonsCard', None).replace(
    'private buildActionButtonsCard()', 'export function WebDavActionButtonsCard(options: WebDavActionOptions)').replace('this.colors', 'options.colors')
actions = actions.replace('this.webdavBusy', 'options.busy').replace('this.webdavBackupResult', 'options.backupResult').replace('this.webdavResult', 'options.configResult')
for method, callback in [('saveWebDavSettings', 'onSave'), ('webdavTest', 'onTest'), ('webdavSyncNow', 'onSync'), ('webdavBackup', 'onBackup'), ('webdavRestore', 'onRestore')]:
    actions = actions.replace('.onClick(async () => { await this.' + method + '(); })', '.onClick(options.' + callback + ')')
for label, node_id in [('保存设置', 'webdav_save_button'), ('测试连接', 'webdav_test_button'), ('立即同步', 'webdav_sync_button'), ('立即备份', 'webdav_backup_button'), ('从云端恢复', 'webdav_restore_button')]:
    actions = actions.replace("Button(options.busy ? '处理中...' : '" + label + "')", "Button(options.busy ? '处理中...' : '" + label + "')\n        .id('" + node_id + "')")
actions = actions.replace('Text(options.configResult)', "Text(options.configResult)\n      .id('webdav_config_result')")
old_result = '''  if (options.backupResult.length > 0) {
    Text(options.backupResult)
      .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
      .fontColor(options.backupResult.includes('✅') ? options.colors.SUCCESS : options.colors.GRAY_600)
      .margin({ top: DesignTokens.Spacing.SM })
      .textAlign(TextAlign.Center)
  }'''
new_result = '''  if (options.backupResult.length > 0) {
    Row({ space: DesignTokens.Spacing.SM }) {
      if (options.backupBusy) {
        LoadingProgress()
          .id('webdav_backup_loading')
          .width(24)
          .height(24)
          .color(options.colors.PRIMARY)
      }
      Text(options.backupResult)
        .id('webdav_backup_status')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.backupResult.includes('✅') ? options.colors.SUCCESS : options.colors.GRAY_600)
        .textAlign(TextAlign.Center)
        .layoutWeight(1)
    }
    .width('100%')
    .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
    .margin({ top: DesignTokens.Spacing.SM })
  }'''
result_start = actions.index('    if (options.backupResult.length > 0)')
result_end = actions.index('    Divider()', result_start)
actions = actions[:result_start] + '\n'.join('  ' + line if line else '' for line in new_result.splitlines()) + '\n\n' + actions[result_end:]

header = '''import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { SelectOption } from './SettingsCommon';

export interface WebDavConfigOptions {
  colors: ColorsInterface;
  disabled: boolean;
  endpoint: string;
  username: string;
  password: string;
  syncPassword: string;
  remoteRoot: string;
  showPassword: boolean;
  showSyncPassword: boolean;
  onEndpointChange: (value: string) => void;
  onUsernameChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onSyncPasswordChange: (value: string) => void;
  onRemoteRootChange: (value: string) => void;
  onTogglePassword: () => void;
  onToggleSyncPassword: () => void;
}

export interface WebDavAutoSyncOptions {
  colors: ColorsInterface;
  enabled: boolean;
  intervalIndex: number;
  uploadModel: boolean;
  uploadBackup: boolean;
  lastSuccessText: string;
  lastError: string;
  onEnabledChange: (value: boolean) => void;
  onIntervalChange: (value: number) => void;
  onUploadModelChange: (value: boolean) => void;
  onUploadBackupChange: (value: boolean) => void;
}

export interface WebDavActionOptions {
  colors: ColorsInterface;
  busy: boolean;
  backupBusy: boolean;
  configResult: string;
  backupResult: string;
  onSave: () => void;
  onTest: () => void;
  onSync: () => void;
  onBackup: () => void;
  onRestore: () => void;
}

const WEBDAV_AUTOSYNC_INTERVAL_OPTIONS: SelectOption[] = [
  { value: '每1小时' }, { value: '每3小时' }, { value: '每6小时（默认）' },
  { value: '每12小时' }, { value: '每24小时' }
];

'''
result = header + input_field + password_field + toggle_row + config + auto + actions
assert 'this.' not in result
assert len(result.splitlines()) <= 500, len(result.splitlines())
(section_path.parent / 'SettingsWebDavBuilders.ets').write_text(result, encoding='utf-8')
source = source[:start] + source[end:]
source = source.replace("import { SelectOption } from './SettingsCommon';", "import { WebDavBasicConfigCard, WebDavAutoSyncCard, WebDavActionButtonsCard } from './SettingsWebDavBuilders';\nimport { ManualWebDavBackupController, ManualWebDavBackupListener, ManualWebDavBackupState } from '../../sync/ManualWebDavBackupController';")
constants_begin = source.index('const WEBDAV_AUTOSYNC_INTERVAL_OPTIONS')
constants_end = source.index('@Component', constants_begin)
source = source[:constants_begin] + source[constants_end:]
section_path.write_text(source, encoding='utf-8')
print('Extracted pure builders:', len(result.splitlines()), 'lines')
