# cml-spec7 最小方案修订 03

版本v1.2；角色 `/root/design_do`；CODEX_THREAD_ID `01a158d2-9ec4-7050-87ff-875ea468f5ce`。仅新增本方案与transport静态复核，不改生产/测试/state。

- **归因：方案生命周期假设缺陷。** 当前MeViewModel将headNavigationPending置true，成功入栈后只在onShown清除；MePage是Main Tab内嵌NavDestination，返回Main未保证该子页onShown再次触发。主Agent独立复现中，新driver、单5555、未dump且已过数分钟仍无法重进；读码可解释入口持续被锁，不能归因400ms去重或传输。
- **唯一生产修改文件：** `feature/main/src/main/ets/viewmodel/MeViewModel.ets`。删除headNavigationPending字段、onShown中的该字段复位，以及onHeadClick内依赖pending/previousSize的置锁与解锁分支；onShown原有refreshPageData保持。
- **替代去重：** 保留lastHeadNavigationAt的同步400ms时间去重；取得getNavPathStack，undefined直接返回。用 `this.userState.isLoggedIn()` 实时计算目标：已登录为 `UserRoutes.Profile`，未登录为 `AuthRoutes.Login`（补AuthRoutes import）；读取 `stack.getAllPathName()`，非空且最后一项等于该实际目标时返回。不要用可能未刷新的this.isLoggedIn或把栈中任意历史项当当前顶层。
- 通过上述检查后先同步记录lastHeadNavigationAt，再调用既有toProfilePage()/navigateTo(UserRoutes.Profile)，由既有拦截完成未登录改写。无跨页面持久bool锁、无新增定时器/共享导航修改；失败后的时间窗口自然到期即可重试，返回Main后顶层已不再是目标，正常允许重进。
- **最小回归：** 同一已安装产物更新后经真实“我的”入口连续执行“进入登录→返回我的→再次进入”至少3轮；点头像及父行快速连点只入栈一次，400ms后旧目标仍在顶层也不得重复推；有合法现有登录态时仍去Profile；缺stack/推送失败后可重试。复核A1、D4/返回重进、E05/E06/E11，随后重跑暂停的完整自测，不把此前A01快照成功当恢复已通过。
- 顶部安全区遵循plan02，38项继续推进；无账号条件下B9–B11真实授权仍未通过。若真实设备仍不重进，再依据新UI/栈证据回退，不扩改共享NavigationService。
