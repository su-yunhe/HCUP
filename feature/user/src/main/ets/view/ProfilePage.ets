import {
  ColumnCenter,
  ColumnStart,
  P100,
  SpaceVerticalLarge,
  SpaceVerticalMedium,
  SpaceVerticalSmall
} from "designsystem";
import { AppNavDestination, Card, SmallAvatar, TitleWithLine } from "ui";
import { IBestCell, IBestCellGroup, IBestDialog } from "ibestui";
import ProfileViewModel from "../viewmodel/ProfileViewModel";

/**
 * @file 个人中心页面视图
 * @author Joker.X
 */
@ComponentV2
export struct ProfilePage {
  /**
   * 个人中心页面 ViewModel
   */
  @Local
  private vm: ProfileViewModel = new ProfileViewModel();

  /**
   * 构建个人中心页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.profile_title"),
      viewModel: this.vm
    }) {
      this.ProfileContent();

      IBestDialog({
        visible: this.vm.showLogoutDialog,
        title: $r("app.string.logout_confirm_title"),
        message: $r("app.string.logout_confirm_message"),
        showCancelButton: true,
        confirmButtonText: $r("app.string.confirm"),
        cancelButtonText: $r("app.string.cancel"),
        onConfirm: (): void => this.vm.confirmLogout(),
        onCancel: (): void => this.vm.hideLogoutDialog(),
        onClose: (): void => this.vm.hideLogoutDialog()
      });
    }
  }

  /**
   * 个人中心页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private ProfileContent(): void {
    Scroll() {
      ColumnStart({
        widthValue: P100,
        paddingValue: {
          left: $r("app.float.space_horizontal_medium"),
          right: $r("app.float.space_horizontal_medium"),
          top: $r("app.float.space_vertical_medium")
        }
      }) {
        this.ProfileBaseInfoCard();

        SpaceVerticalMedium();
        SpaceVerticalSmall();
        this.SectionTitle($r("app.string.account_info"));
        SpaceVerticalMedium();
        this.AccountInfoCard();

        SpaceVerticalMedium();
        SpaceVerticalSmall();
        this.SectionTitle($r("app.string.social_account"));
        SpaceVerticalMedium();
        this.SocialAccountCard();

        SpaceVerticalMedium();
        SpaceVerticalSmall();
        this.SectionTitle($r("app.string.security"));
        SpaceVerticalMedium();
        this.SecurityCard();

        SpaceVerticalMedium();

        this.LogoutCard();
      }
    }
    .scrollBar(BarState.Off);
  }

  /**
   * 基础信息卡片
   * @returns {void} 无返回值
   */
  @Builder
  private ProfileBaseInfoCard(): void {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          title: $r("app.string.avatar"),
          label: $r("app.string.avatar_label"),
          hasBorder: true,
          isLink: false,
          cellPadding: $r("app.float.space_padding_medium"),
          rightIconBuilder: (): void => this.AvatarRightContent()
        });

        IBestCell({
          title: $r("app.string.nickname"),
          value: this.vm.getNickNameText(),
          hasBorder: false,
          isLink: false,
          cellPadding: $r("app.float.space_padding_large")
        });
      }
    }
  }

  /**
   * 账号信息卡片
   * @returns {void} 无返回值
   */
  @Builder
  private AccountInfoCard(): void {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          title: $r("app.string.phone"),
          value: this.vm.getPhoneText(),
          hasBorder: true,
          isLink: false,
          cellPadding: $r("app.float.space_padding_large")
        });

        IBestCell({
          title: $r("app.string.account"),
          value: this.vm.getAccountText(),
          hasBorder: false,
          isLink: false,
          cellPadding: $r("app.float.space_padding_large")
        });
      }
    }
  }

  /**
   * 社交账号卡片
   * @returns {void} 无返回值
   */
  @Builder
  private SocialAccountCard(): void {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          title: $r("app.string.wechat"),
          value: $r("app.string.go_bind"),
          hasBorder: true,
          isLink: false,
          cellPadding: $r("app.float.space_padding_large")
        });

        IBestCell({
          title: $r("app.string.qq"),
          value: $r("app.string.bound"),
          hasBorder: false,
          isLink: false,
          cellPadding: $r("app.float.space_padding_large")
        });
      }
    }
  }

  /**
   * 安全设置卡片
   * @returns {void} 无返回值
   */
  @Builder
  private SecurityCard(): void {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          title: $r("app.string.change_password"),
          hasBorder: true,
          isLink: true,
          cellPadding: $r("app.float.space_padding_large")
        });

        IBestCell({
          title: $r("app.string.delete_account"),
          hasBorder: false,
          isLink: true,
          cellPadding: $r("app.float.space_padding_large")
        });
      }
    }
  }

  /**
   * 退出登录卡片
   * @returns {void} 无返回值
   */
  @Builder
  private LogoutCard(): void {
    Card({
      onTap: (): void => this.vm.onLogoutClick()
    }) {
      ColumnCenter({
        widthValue: P100,
        paddingValue: $r("app.float.space_padding_large")
      }) {
        Text($r("app.string.logout"))
          .fontSize($r("app.float.body_large"))
          .fontColor($r("app.color.danger"));
      }
    }
  }

  /**
   * 区块标题
   * @param {ResourceStr} title - 标题文本
   * @returns {void} 无返回值
   */
  @Builder
  private SectionTitle(title: ResourceStr): void {
    TitleWithLine({
      text: title,
    });
  }

  /**
   * 头像右侧内容
   * @returns {void} 无返回值
   */
  @Builder
  private AvatarRightContent(): void {
    SmallAvatar({
      src: this.vm.getAvatarUrl()
    });
  }
}
