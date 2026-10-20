import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';

@Component
export struct SettingsSyncConfigCard {
  @Link webdavEndpoint: string;
  @Link webdavUsername: string;
  @Link webdavPassword: string;
  @Link webdavSyncPassword: string;
  @Link webdavRemoteRoot: string;
  @Link showWebdavPassword: boolean;
  @Link showWebdavSyncPassword: boolean;
  @StorageProp('ThemeRefreshToken') @Watch('onThemeChange') themeRefreshToken: number = 0;
  @State private colors: ColorsInterface = ThemeManager.getInstance().getColors();

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  @Builder
  private buildInputField(controlId: string, label: string, value: string, placeholder: string, onChange: (val: string) => void) {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      TextInput({ text: value, placeholder })
        .id(controlId)
        .width('100%')
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .backgroundColor(this.colors.GRAY_100)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.MD })
        .onChange(onChange)
    }
    .width('100%')
    .margin({ bottom: DesignTokens.Spacing.MD })
  }

  @Builder
  private buildPasswordField(controlId: string, label: string, value: string, placeholder: string, isVisible: boolean, onChange: (val: string) => void, onToggle: () => void) {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      Row() {
        TextInput({ text: value, placeholder })
          .id(controlId)
          .type(isVisible ? InputType.Normal : InputType.Password)
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .backgroundColor(this.colors.GRAY_100)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.SM })
          .onChange(onChange)

        Button(isVisible ? '隐藏' : '显示')
          .margin({ left: DesignTokens.Spacing.SM })
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_700)
          .backgroundColor(this.colors.GRAY_200)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .onClick(onToggle)
      }
      .width('100%')
    }
    .width('100%')
    .margin({ bottom: DesignTokens.Spacing.MD })
  }

  build() {
    Column() {
      Text('基础配置')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      this.buildInputField('webdav_endpoint_input', 'WebDAV 地址', this.webdavEndpoint, 'https://dav.example.com/dav/', (v) => this.webdavEndpoint = v)
      this.buildInputField('webdav_username_input', '账号', this.webdavUsername, 'username', (v) => this.webdavUsername = v)
      this.buildPasswordField('webdav_password_input', '密码', this.webdavPassword, 'password', this.showWebdavPassword, (v) => this.webdavPassword = v, () => this.showWebdavPassword = !this.showWebdavPassword)
      this.buildPasswordField('webdav_sync_password_input', '同步密码（用于 AES 加密）', this.webdavSyncPassword, 'sync password', this.showWebdavSyncPassword, (v) => this.webdavSyncPassword = v, () => this.showWebdavSyncPassword = !this.showWebdavSyncPassword)
      this.buildInputField('webdav_remote_root_input', '远端目录', this.webdavRemoteRoot, '/weiyu_sync', (v) => this.webdavRemoteRoot = v)

      Text('提示：请先在 WebDAV 服务端创建该目录（只需一次）')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_500)
        .width('100%')
    }
    .width('100%')
    .padding(DesignTokens.Spacing.LG)
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
  }

}
