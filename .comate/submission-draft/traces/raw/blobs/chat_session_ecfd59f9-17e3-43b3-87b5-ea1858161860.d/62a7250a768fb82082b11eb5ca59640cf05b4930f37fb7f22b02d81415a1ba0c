import Constants from "../../common/constants/Constants"
import { StorageConstants } from "../../common/constants/StorageConstants"
import { ApiConfig } from "../../common/entities/local/Settings"
import { getApiConfig, saveApiConfig } from "../../common/functions/app/settings"

const LABEL_WIDTH: number = 50
const INPUT_HEIGHT: number = 36
const ROW_SPACE: number = 6

/**
 * 在线服务配置表单
 * 设置页「在线服务」与发现页底部配置面板共用
 */
@Component
export struct ApiConfigForm {
  @StorageProp(StorageConstants.VALID_API_URL) validApiUrl: boolean = false
  @State protocol: string = 'http'
  @State host: string = ''
  @State port: string = ''
  @State path: string = ''
  @State user: string = ''
  @State password: string = ''
  // 保存后回调（如关闭面板）
  onSaved?: () => void

  aboutToAppear(): void {
    this.loadConfig()
  }

  // 布局紧凑，保证软键盘弹出时"保存配置"按钮仍在可见区域内
  build() {
    Column({ space: ROW_SPACE }) {
      this.Fields()
      this.SaveButton()
    }
    .width('100%')
  }

  @Builder Fields() {
    Column({ space: ROW_SPACE }) {
      Row() {
        Text('连通性状态').LabelText()
        Text(this.validApiUrl ? '正常' : '不可用')
          .id('api_status')
          .fontSize(Constants.FONT_SIZE_COMMON)
          .fontWeight(FontWeight.Bold)
          .fontColor(this.validApiUrl ? Color.Green : $r('app.color.app_red'))
      }
      .width('100%')
      .justifyContent(FlexAlign.SpaceBetween)

      Row({ space: 10 }) {
        Text('主机').LabelText().width(LABEL_WIDTH)
        TextInput({ text: this.host, placeholder: '域名或IP地址' })
          .id('api_host_input')
          .InputStyle()
          .onChange((text) => this.host = text)
      }
      .width('100%')

      Row({ space: 10 }) {
        Text('端口').LabelText().width(LABEL_WIDTH)
        TextInput({ text: this.port, placeholder: '留空使用协议默认端口' })
          .id('api_port_input')
          .InputStyle()
          .type(InputType.Number)
          .maxLength(5)
          .onChange((text) => this.port = text)
      }
      .width('100%')

      Row({ space: 10 }) {
        Text('请求').LabelText().width(LABEL_WIDTH)
        Row() {
          Radio({ value: 'HTTP', group: 'apiProtocol' })
            .id('api_protocol_http')
            .checked(this.protocol === 'http')
            .radioStyle({ checkedBackgroundColor: $r('app.color.app_red') })
            .onChange((isChecked) => {
              if (isChecked) this.protocol = 'http'
            })
          Text('HTTP')
            .OptionText()
            .padding({ right: 20 })
            .onClick(() => this.protocol = 'http')
          Radio({ value: 'HTTPS', group: 'apiProtocol' })
            .id('api_protocol_https')
            .checked(this.protocol === 'https')
            .radioStyle({ checkedBackgroundColor: $r('app.color.app_red') })
            .onChange((isChecked) => {
              if (isChecked) this.protocol = 'https'
            })
          Text('HTTPS')
            .OptionText()
            .onClick(() => this.protocol = 'https')
        }
        .layoutWeight(1)
      }
      .width('100%')
      .height(INPUT_HEIGHT)

      Row({ space: 10 }) {
        Text('路径').LabelText().width(LABEL_WIDTH)
        TextInput({ text: this.path, placeholder: '无部署前缀时留空' })
          .id('api_path_input')
          .InputStyle()
          .onChange((text) => this.path = text)
      }
      .width('100%')

      Row({ space: 10 }) {
        Text('用户').LabelText().width(LABEL_WIDTH)
        TextInput({ text: this.user, placeholder: '未配置认证时留空' })
          .id('api_user_input')
          .InputStyle()
          .onChange((text) => this.user = text)
      }
      .width('100%')

      Row({ space: 10 }) {
        Text('密码').LabelText().width(LABEL_WIDTH)
        TextInput({ text: this.password, placeholder: '未配置认证时留空' })
          .id('api_password_input')
          .InputStyle()
          .type(InputType.Password)
          .onChange((text) => this.password = text)
      }
      .width('100%')
    }
    .width('100%')
  }

  @Builder SaveButton() {
    Button('保存配置')
      .id('api_save_button')
      .fontSize(Constants.FONT_SIZE_COMMON)
      .fontColor($r('app.color.app_red'))
      .borderColor($r('app.color.app_red'))
      .backgroundColor(Color.Transparent)
      .borderWidth(1)
      .width(150)
      .padding({ left: Constants.PADDING_EDGE_DEFAULT, right: Constants.PADDING_EDGE_DEFAULT })
      .onClick(() => {
        this.save()
      })
  }

  private loadConfig() {
    const config = getApiConfig()
    this.protocol = config.protocol
    this.host = config.host
    this.port = config.port
    this.path = config.path
    this.user = config.user
    this.password = config.password
  }

  private save() {
    const config: ApiConfig = {
      protocol: this.protocol,
      host: this.host,
      port: this.port,
      path: this.path,
      user: this.user,
      password: this.password
    }
    saveApiConfig(config)
    // 回显规范化后的已保存值
    this.loadConfig()
    this.onSaved?.()
  }
}

@Extend(Text) function LabelText() {
  .fontSize(Constants.FONT_SIZE_COMMON)
  .fontWeight(FontWeight.Bold)
  .fontColor($r('app.color.reverse'))
}

@Extend(Text) function OptionText() {
  .fontSize(Constants.FONT_SIZE_COMMON)
  .fontColor($r('app.color.reverse'))
}

@Extend(TextInput) function InputStyle() {
  .layoutWeight(1)
  .height(INPUT_HEIGHT)
  .borderRadius(Constants.RADIUS_IMG)
}
