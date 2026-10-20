import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { SelectOption } from './SettingsCommon';

interface WebDavInputOptions {
  colors: ColorsInterface;
  disabled: boolean;
  inputId: string;
  label: string;
  value: string;
  placeholder: string;
  onChange: (value: string) => void;
}

interface WebDavPasswordOptions extends WebDavInputOptions {
  isVisible: boolean;
  onToggle: () => void;
}

interface WebDavToggleOptions {
  colors: ColorsInterface;
  title: string;
  subtitle: string;
  isOn: boolean;
  onChange: (value: boolean) => void;
}

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

@Builder
function WebDavInputField(options: WebDavInputOptions) {
  Column() {
    Text(options.label)
      .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
      .fontColor(options.colors.GRAY_600)
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.XS })

    TextInput({ text: options.value, placeholder: options.placeholder })
      .width('100%')
      .height(44)
      .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
      .backgroundColor(options.colors.GRAY_100)
      .borderRadius(DesignTokens.BorderRadius.MD)
      .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.MD })
      .id(options.inputId)
      .enabled(!options.disabled)
      .onChange(options.onChange)
  }
  .width('100%')
  .margin({ bottom: DesignTokens.Spacing.MD })
}

@Builder
function WebDavPasswordField(options: WebDavPasswordOptions) {
  Column() {
    Text(options.label)
      .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
      .fontColor(options.colors.GRAY_600)
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.XS })

    Row() {
      TextInput({ text: options.value, placeholder: options.placeholder })
        .type(options.isVisible ? InputType.Normal : InputType.Password)
        .layoutWeight(1)
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .backgroundColor(options.colors.GRAY_100)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.SM })
        .id(options.inputId)
        .enabled(!options.disabled)
        .onChange(options.onChange)

      Button(options.isVisible ? '隐藏' : '显示')
        .margin({ left: DesignTokens.Spacing.SM })
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.GRAY_700)
        .backgroundColor(options.colors.GRAY_200)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .enabled(!options.disabled)
        .onClick(options.onToggle)
    }
    .width('100%')
  }
  .width('100%')
  .margin({ bottom: DesignTokens.Spacing.MD })
}

@Builder
function WebDavToggleRow(options: WebDavToggleOptions) {
  Row() {
    Column() {
      Text(options.title)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(options.colors.GRAY_700)
      Text(options.subtitle)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.GRAY_600)
    }
    .alignItems(HorizontalAlign.Start)

    Blank()

    Toggle({ type: ToggleType.Switch, isOn: options.isOn })
      .selectedColor(options.colors.PRIMARY)
      .switchPointColor(options.colors.WHITE)
      .onChange(options.onChange)
  }
  .width('100%')
  .height(64)
  .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
}

@Builder
export function WebDavBasicConfigCard(options: WebDavConfigOptions) {
  Column() {
    Text('基础配置')
      .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
      .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
      .fontColor(options.colors.TEXT_PRIMARY)
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.MD })

    WebDavInputField({
      colors: options.colors, disabled: options.disabled, inputId: 'webdav_endpoint_input',
      label: 'WebDAV 地址', value: options.endpoint, placeholder: 'https://dav.example.com/dav/',
      onChange: options.onEndpointChange
    })
    WebDavInputField({
      colors: options.colors, disabled: options.disabled, inputId: 'webdav_username_input',
      label: '账号', value: options.username, placeholder: 'username', onChange: options.onUsernameChange
    })
    WebDavPasswordField({
      colors: options.colors, disabled: options.disabled, inputId: 'webdav_password_input',
      label: '密码', value: options.password, placeholder: 'password', isVisible: options.showPassword,
      onChange: options.onPasswordChange, onToggle: options.onTogglePassword
    })
    WebDavPasswordField({
      colors: options.colors, disabled: options.disabled, inputId: 'webdav_sync_password_input',
      label: '同步密码（用于 AES 加密）', value: options.syncPassword, placeholder: 'sync password',
      isVisible: options.showSyncPassword, onChange: options.onSyncPasswordChange,
      onToggle: options.onToggleSyncPassword
    })
    WebDavInputField({
      colors: options.colors, disabled: options.disabled, inputId: 'webdav_remote_root_input',
      label: '远端目录', value: options.remoteRoot, placeholder: '/weiyu_sync', onChange: options.onRemoteRootChange
    })

    Text('提示：请先在 WebDAV 服务端创建该目录（只需一次）')
      .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
      .fontColor(options.colors.GRAY_500)
      .width('100%')
  }
  .width('100%')
  .padding(DesignTokens.Spacing.LG)
  .backgroundColor(options.colors.SURFACE_PRIMARY)
  .borderRadius(DesignTokens.BorderRadius.LG)
}

@Builder
export function WebDavAutoSyncCard(options: WebDavAutoSyncOptions) {
  Column() {
    Text('自动同步')
      .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
      .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
      .fontColor(options.colors.TEXT_PRIMARY)
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.MD })

    WebDavToggleRow({
      colors: options.colors, title: '启用自动同步', subtitle: '进入前台时按间隔自动同步',
      isOn: options.enabled, onChange: options.onEnabledChange
    })

    if (options.enabled) {
      Divider().color(options.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      Row() {
        Text('同步间隔')
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(options.colors.GRAY_700)
        Blank()
        Select(WEBDAV_AUTOSYNC_INTERVAL_OPTIONS)
          .selected(options.intervalIndex)
          .value(WEBDAV_AUTOSYNC_INTERVAL_OPTIONS[options.intervalIndex].value)
          .font({ size: DesignTokens.Typography.FONT_SIZE_BASE })
          .fontColor(options.colors.GRAY_700)
          .onSelect(options.onIntervalChange)
      }
      .width('100%')
      .height(56)
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      Divider().color(options.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      WebDavToggleRow({
        colors: options.colors, title: '自动上传模型', subtitle: '用于多端算法同步',
        isOn: options.uploadModel, onChange: options.onUploadModelChange
      })

      Divider().color(options.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      WebDavToggleRow({
        colors: options.colors, title: '自动上传全量备份', subtitle: '只上传，不自动恢复覆盖本地',
        isOn: options.uploadBackup, onChange: options.onUploadBackupChange
      })

      Column() {
        Text(`上次自动同步：${options.lastSuccessText}`)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(options.colors.GRAY_500)
          .width('100%')

        if (options.lastError.length > 0) {
          Text(`最近错误：${options.lastError}`)
            .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
            .fontColor(options.colors.ERROR)
            .width('100%')
            .margin({ top: DesignTokens.Spacing.XS })
        }
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.SM })
    }
  }
  .width('100%')
  .padding({ top: DesignTokens.Spacing.LG, bottom: DesignTokens.Spacing.LG })
  .backgroundColor(options.colors.SURFACE_PRIMARY)
  .borderRadius(DesignTokens.BorderRadius.LG)
  .margin({ top: DesignTokens.Spacing.MD })
}

@Builder
export function WebDavActionButtonsCard(options: WebDavActionOptions) {
  Column() {
    Text('手动操作')
      .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
      .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
      .fontColor(options.colors.TEXT_PRIMARY)
      .width('100%')
      .margin({ bottom: DesignTokens.Spacing.MD })

    Row() {
      Button(options.busy ? '处理中...' : '保存设置')
        .id('webdav_save_button')
        .layoutWeight(1)
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(options.colors.WHITE)
        .backgroundColor(options.busy ? options.colors.GRAY_400 : options.colors.GRAY_600)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .enabled(!options.busy)
        .onClick(options.onSave)

      Button(options.busy ? '处理中...' : '测试连接')
        .id('webdav_test_button')
        .layoutWeight(1)
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(options.colors.WHITE)
        .backgroundColor(options.busy ? options.colors.GRAY_400 : options.colors.PRIMARY)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .enabled(!options.busy)
        .margin({ left: DesignTokens.Spacing.SM })
        .onClick(options.onTest)
    }
    .width('100%')
    .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

    if (options.configResult.length > 0) {
      Text(options.configResult)
        .id('webdav_config_result')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.configResult.includes('✅') ? options.colors.SUCCESS : options.colors.GRAY_600)
        .margin({ top: DesignTokens.Spacing.SM })
        .textAlign(TextAlign.Center)
    }

    Divider().color(options.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

    Row() {
      Button(options.busy ? '处理中...' : '立即同步')
        .id('webdav_sync_button')
        .layoutWeight(1)
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(options.colors.WHITE)
        .backgroundColor(options.busy ? options.colors.GRAY_400 : options.colors.PRIMARY)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .enabled(!options.busy)
        .onClick(options.onSync)
    }
    .width('100%')
    .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

    Divider().color(options.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

    Row() {
      Button(options.busy ? '处理中...' : '立即备份')
        .id('webdav_backup_button')
        .layoutWeight(1)
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(options.colors.WHITE)
        .backgroundColor(options.busy ? options.colors.GRAY_400 : options.colors.SUCCESS)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .enabled(!options.busy)
        .onClick(options.onBackup)

      Button(options.busy ? '处理中...' : '从云端恢复')
        .id('webdav_restore_button')
        .layoutWeight(1)
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(options.colors.WHITE)
        .backgroundColor(options.busy ? options.colors.GRAY_400 : options.colors.ERROR)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .enabled(!options.busy)
        .margin({ left: DesignTokens.Spacing.SM })
        .onClick(options.onRestore)
    }
    .width('100%')
    .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

    if (options.backupResult.length > 0) {
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
    }

    Divider().color(options.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

    Text('使用说明')
      .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
      .fontColor(options.colors.TEXT_SECONDARY)
      .margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

    Column() {
      Text('【立即同步】日常多端同步，只同步变更数据')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.TEXT_SECONDARY)
        .width('100%')
      Text('• 同步学习过的单词、复习记录、用户词书')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.GRAY_500)
        .width('100%')
        .margin({ left: DesignTokens.Spacing.SM })
      Text('• 未学习的单词不会同步，节省流量')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.GRAY_500)
        .width('100%')
        .margin({ left: DesignTokens.Spacing.SM })
      Text('【立即备份】完整备份所有数据到云端')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.TEXT_SECONDARY)
        .width('100%')
        .margin({ top: DesignTokens.Spacing.SM })
      Text('• 适合换设备前、定期备份使用')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.GRAY_500)
        .width('100%')
        .margin({ left: DesignTokens.Spacing.SM })
      Text('【从云端恢复】下载云端数据覆盖本地')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.TEXT_SECONDARY)
        .width('100%')
        .margin({ top: DesignTokens.Spacing.SM })
      Text('• ⚠️ 会覆盖本地数据，新设备首次使用')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.GRAY_500)
        .width('100%')
        .margin({ left: DesignTokens.Spacing.SM })
      Text('• 本地未同步的学习记录将丢失')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(options.colors.GRAY_500)
        .width('100%')
        .margin({ left: DesignTokens.Spacing.SM })
    }
    .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.SM })
    .width('100%')
  }
  .width('100%')
  .padding({ top: DesignTokens.Spacing.LG, bottom: DesignTokens.Spacing.LG })
  .backgroundColor(options.colors.SURFACE_PRIMARY)
  .borderRadius(DesignTokens.BorderRadius.LG)
  .margin({ top: DesignTokens.Spacing.MD })
}

