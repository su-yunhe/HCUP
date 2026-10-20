# cml-spec7 最小方案修订 02

版本 v1.1（替代v1.0顶部安全区位置）；角色 `/root/design_do`；CODEX_THREAD_ID `01a158d2-9ec4-7050-87ff-875ea468f5ce`。

- **归因：方案缺陷。** 已查看 `logs/verification-phone-preview-01/phone-login-after-permission.jpeg`，返回按钮与系统时间04:34重叠，标题处于状态栏同一行。当前LoginPage按v1.0传 `paddingValue:0`，只对内容根加topInset；AppNavDestination的内建title位于其内容外，因此未被该避让保护，实现未偏离原方案。
- **唯一生产修改文件：** `feature/auth/src/main/ets/view/LoginPage.ets`。保留 `safeAreaEnabled:false`，把AppNavDestination参数改为 `paddingValue:{top:this.safeArea.topInset,left:0,right:0,bottom:0}`，令整个NavDestination（含内建标题/返回）避开顶部状态栏。
- **内部对应调整：** `auth_login_page` 的padding改为 `top:0`，left/right/bottom继续读取safeArea各自inset；不增加额外标题高度或固定顶部间距。topInset只在外层应用一次，左右/bottom仍只在内部应用一次。不改共享AppNavDestination、WindowSafeAreaState或其他页面。
- **契约保持：** page/content/region的横向边界、无业务padding的可用宽度分母与100%/70%/60%居中规则不变；page纵向坐标现在位于避让后的标题内容区，验证记录应以本次实际边界为准。继续由实际Scroll视口更新minHeight，避免修顶部时产生双重留白或页脚裁切。
- **受影响验证：** 重构建/安装后取真实手机截图和UI树，确认系统时间/状态图标与返回按钮/“登录”标题无重叠、返回可点；复查A3/A4/A5顶部Logo与中心/尺寸、B17页脚底部和短高可滚到；抽测C1–C7宽度/居中/间距保持及旋转或窗口变化时topInset不重复。未运行这些检查前不宣称修复通过。
- **范围继续：** 38项可实现需求继续推进；用户现说明没有账号，B9–B11真实第三方授权仍受合法平台配置/账号条件阻塞，缺配置反馈不算真实授权通过。本角色只新增此设计文件，未改生产、测试或state。
