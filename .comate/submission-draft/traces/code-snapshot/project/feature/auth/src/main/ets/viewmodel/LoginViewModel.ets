import { BaseViewModel } from "base";
import { AuthRoutes, CommonRoutes, getNavPathStack, navigateToWithResult } from "navigation";

export enum LoginProvider {
  Wechat,
  QQ,
  Alipay
}

/**
 * @file 登录页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class LoginViewModel extends BaseViewModel {
  @Trace
  errorMessage: ResourceStr = "";

  private visible: boolean = true;
  private navigationPending: boolean = false;
  private operationId: number = 0;
  private lastNavigationAt: number = 0;
  private lastProviderAt: number = 0;
  private lastProvider: LoginProvider | undefined = undefined;

  onShown(reason: VisibilityChangeReason): void {
    super.onShown(reason);
    this.visible = true;
    this.navigationPending = false;
    this.operationId++;
  }

  onHidden(reason: VisibilityChangeReason): void {
    super.onHidden(reason);
    this.invalidateOperation();
  }

  aboutToBeDeleted(): void {
    this.invalidateOperation();
    super.aboutToBeDeleted();
  }

  toSmsLogin(): void {
    this.openRoute(AuthRoutes.SmsLogin);
  }

  toAccountLogin(): void {
    this.openRoute(AuthRoutes.AccountLogin);
  }

  toUserAgreement(): void {
    this.openRoute(CommonRoutes.UserAgreement);
  }

  toPrivacyPolicy(): void {
    this.openRoute(CommonRoutes.PrivacyPolicy);
  }

  /** Only availability is checked here; no authorization or authentication is fabricated. */
  startProviderLogin(provider: LoginProvider): void {
    if (!this.visible || this.navigationPending) {
      return;
    }
    const now: number = Date.now();
    if (this.lastProvider === provider && now - this.lastProviderAt < 400) {
      return;
    }
    this.lastProvider = provider;
    this.lastProviderAt = now;
    // No registered provider configuration or credential exchange contract is present.
    switch (provider) {
      case LoginProvider.Wechat:
        this.errorMessage = $r("app.string.login_wechat_unavailable");
        break;
      case LoginProvider.QQ:
        this.errorMessage = $r("app.string.login_qq_unavailable");
        break;
      case LoginProvider.Alipay:
        this.errorMessage = $r("app.string.login_alipay_unavailable");
        break;
    }
  }

  private openRoute(route: string): void {
    const now: number = Date.now();
    if (!this.visible || this.navigationPending || now - this.lastNavigationAt < 400) {
      return;
    }
    this.navigationPending = true;
    this.lastNavigationAt = now;
    this.errorMessage = "";
    const operation: number = ++this.operationId;
    const stack: NavPathStack | undefined = getNavPathStack();
    if (stack === undefined) {
      this.finishNavigation(operation, false);
      return;
    }
    const previousSize: number = stack.size();
    navigateToWithResult(route)
      .then((): void => {
        this.finishNavigation(operation, stack.size() > previousSize);
      })
      .catch((): void => {
        this.finishNavigation(operation, false);
      });
  }

  private finishNavigation(operation: number, succeeded: boolean): void {
    if (operation !== this.operationId || !this.visible) {
      return;
    }
    this.navigationPending = false;
    if (!succeeded) {
      this.errorMessage = $r("app.string.login_navigation_failed");
    }
  }

  private invalidateOperation(): void {
    this.visible = false;
    this.navigationPending = false;
    this.operationId++;
  }
}
