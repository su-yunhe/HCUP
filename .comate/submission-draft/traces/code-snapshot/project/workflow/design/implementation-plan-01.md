# cml-spec7 实施方案 01

版本 v1.0，2026-10-20；角色 `/root/design_do`；原生 `CODEX_THREAD_ID=01a158d2-9ec4-7050-87ff-875ea468f5ce`。
基线 `75fd0066a7fc0c1e8cedb6218df081f86d307f45`。本角色只写本方案，不改源码、测试、全局state或操作构建/设备。

## 1. 输入、覆盖与实现边界

已读本题 requirement、metadata、acceptance、baseline-notes、analysis-review及用户新授权修订后的 `workflow/requirements/implementation-review-01.md`；需求复审SHA256 `4cc846246669fd576776a1cdf28660a55198e60b8c48da7820041285235497cf`。仅使用本题源码/记录，无其他题、上游实现/修复历史或初始化总览会话。
41项全部保留：A1–A15、B1–B8、B12–B19、C1–C7共38项可以完整实施；B9–B11先实现可点击、缺配置反馈、去重和恢复，真实授权缺口仍不算通过。
用户新授权允许原创本应用协议，因此B14/B15直接实施本地正文，无需等待外部URL。三方官方SDK、合法配置和回调适配由主Agent按 `workflow/provider-research-01.md` 推进，可另补v1.1，不阻塞38项。
沿用“我的”受保护入口、现有路由/VM/容器/Logo/主题/断点。短信和账号目标页只需真实导航、稳定id及可辨认内容，不扩写发送验证码、密码认证或登录态业务。

## 2. 源码入口与状态流证据

- `MainPage.ets:71` 第4个Tab为MePage；`MePage.ets:102–115` 资料行/头像均调onHeadClick；`MeViewModel.ets:269–270` 去个人资料，`NavigationService.ets:56–73` 未登录改写到auth/login。保留已登录分支，防止头像与父行/连点重复入栈。
- LoginPage/LoginViewModel是占位页/空VM；AuthRoutes的Login/SmsLogin/AccountLogin及CommonRoutes的UserAgreement/PrivacyPolicy已注册，无需新路由/图或入口。
- AppNavDestination转发onShown/onHidden、默认加安全区padding；BaseViewModel已有生命周期钩子。LogoIcon.iconSize标vp，CommonIcon宽高相等；designsystem有P100/P70/P60、primary和间距/圆角资源。
- BreakpointState严格按 `<320/<600/<840/其他` 分段，WindowAdapter已监听窗口变化并按密度换算vp。AuthRepository只提供微信/QQ候选POST；QQ参数为accessToken/openId，支付宝证据仅支付。协议页为空，getParam没有协议key。
- 数据流：真实入口→拦截→登录页；四个普通操作→VM→既有目标路由→返回恢复。三方→provider可用性检查→当前缺配置错误，不到认证/持久化。两协议→本地资源→Scroll/Text，无HTTP。

## 3. 精确改动范围与接口

| 文件（均相对本题根） | 最小修改 |
| --- | --- |
| `feature/auth/src/main/ets/view/LoginPage.ets` | 完整主UI、真实几何节点、Logo/双按钮/三方、滚动页脚、错误分支及id |
| `feature/auth/src/main/ets/viewmodel/LoginViewModel.ets` | 四路导航、provider明确类型/配置检查、局部去重、可见性/操作序号与错误恢复 |
| `feature/auth/src/main/resources/base/element/string.json` | 新增主页专用“手机号登录”“登录即代表同意”和必要错误文案；复用其余准确资源 |
| `feature/auth/src/main/resources/base/media/ic_login_wechat.svg`、`ic_login_qq.svg`、`ic_login_alipay.svg` | 本地可辨识三品牌图标；不能只用文字当图案 |
| `feature/auth/src/main/ets/view/SmsLoginPage.ets`、`AccountLoginPage.ets` | 真实目标页id及“手机短信验证码登录”/“账号密码登录”可辨认内容 |
| `feature/main/src/main/ets/view/MainPage.ets`、`MePage.ets` | 真实“我的”页签/资料入口补id；其余Tab如设id须各自唯一 |
| `feature/main/src/main/ets/viewmodel/MeViewModel.ets` | 仅onHeadClick同步防重、onShown恢复；保留现有刷新与分流 |
| `feature/common/src/main/ets/view/UserAgreementPage.ets`、`PrivacyPolicyPage.ets` | 各自page/content id、本地Scroll正文替换占位 |
| `feature/common/src/main/resources/base/element/string.json` | 原创两正文、版本/日期；必要时同步新增key的en资源 |

局部接口为toSmsLogin/toAccountLogin/toUserAgreement/toPrivacyPolicy/startProviderLogin(provider)，可按项目风格等价命名。不改路由/网络/存储契约；静态正文无需新仓库或修改协议VM。真实SDK适配所需依赖/配置/Ability回调另按主Agent核验来源补范围，不造空成功适配器。

## 4. 几何、内容与稳定id

U1/U3采用：窗口逻辑宽度w<600vp→100%，600≤w<840→70%，w≥840→60%；比例/居中分母统一为安全区内、业务水平padding前的可用页面外框。横屏/分屏按当前窗口分类，无最大宽度上限。
LoginPage局部令AppNavDestination不自动padding（safeAreaEnabled:false、paddingValue:0）；内部真实100%原生根`auth_login_page`加四边安全区padding，其内100%无业务padding的`auth_login_content`成为可用外框。只应用一次安全区，保留标题/返回，不修改共享容器默认值。两个节点的真实边界分别可测。
content内放全尺寸Scroll，滚动Column最小高度取实际可用视口高度（尺寸回调更新），自然高度可更大；顶部主区+可伸缩中间空白+末尾页脚。长屏页脚靠底，短屏全内容可滚到且无重叠；不能只在无限滚动约束内靠layoutWeight或固定高度撑页脚。
LogoIcon({iconSize:120})置顶部、双按钮前，真实120×120vp边界居中于content。按钮与三方共用`auth_login_button_region`外框，bp取XS/SM:P100、MD:P70、LG:P60并居中；该外框无预先缩小的margin/padding，内层另加常规留白。C1测外框100%，不以按钮自身边缘取代区域。
顺序为Logo→实心圆角“手机号登录”→空心描边圆角“账号密码登录”→“其他登录方式”→三图标/标签→真实错误（若有）。用既有primary/背景/文本/圆角/间距资源。
三方Row内放3个layoutWeight(1)等宽Column，每列同尺寸图标点击区、同图像尺寸及标签间距、水平居中；标签自然宽度不能决定列宽。“微信”“QQ”“支付宝”分别在对应图标下方。窄屏/字体变化均不得裁切或溢出区域。
页脚精确拼接`登录即代表同意《用户协议》和《隐私政策》`；不复用旧prefix“登录即代表您已阅读并同意”或用“验证码登录”代主按钮。用可换行Flex中的真实独立Text（prefix/两链接/和），两链接primary且独立点击；不造不可见完整句。若改用Span，必须设备证明独立定位点击，否则退回独立Text。

| 稳定id | 真实节点 |
| --- | --- |
| `main_tab_me` / `me_login_entry` | 真实页签/资料入口点击区 |
| `auth_login_page` / `auth_login_content` / `auth_login_scroll` | 安全区前外框/可用外框/Scroll视口 |
| `auth_login_logo` / `auth_login_button_region` | Logo120方形/包含按钮和三方的比例外框 |
| `auth_login_phone` / `auth_login_account` | 两真实按钮 |
| `auth_login_other_methods` / `auth_login_social_row` | 真实提示/等宽三列所属行 |
| `auth_login_{wechat,qq,alipay}_icon` / `auth_login_{wechat,qq,alipay}_label` | 各同尺寸真实图标点击区/对应标签（花括号展开成6个id） |
| `auth_login_provider_state` / `auth_login_error` | 有错误时可见状态容器/错误Text |
| `auth_login_agreement_footer` / `auth_login_user_agreement` / `auth_login_privacy_policy` | 完整真实页脚/独立链接Text |
| `auth_sms_login_page` / `auth_account_login_page` | 两既有目标页真实可辨根 |
| `common_user_agreement_page` / `common_user_agreement_content` | 对应页根/真实协议正文 |
| `common_privacy_policy_page` / `common_privacy_policy_content` | 对应页根/真实隐私正文 |

自定义组件id须实查UI树；不透传时用真实原生包裹节点。不渲染无业务依据的loading节点。

## 5. 导航、配置检查与网络状态

导航处理器先同步置navigationPending再推现有路由；推送期间合并连点并阻止三方穿插。复用onShown/onHidden/销毁钩子、局部visible/operationId，导航失败/返回均恢复；处理未初始化stack及navigateTo系列吞错的情况，不能只靠catch永久挂锁。Me入口同步防重覆盖头像/父行双回调，onShown恢复。
三方使用明确provider枚举及可观察错误字段，缺配置检查同步完成，不假装授权中。局部最近点击时间（如400ms，设计值）可合并缺配置连点；错误后两普通按钮、其他provider、协议和返回仍可操作，不叠弹窗/任务。产品提示如“微信登录暂不可用，请使用手机号或账号密码登录”，内部记录原因configuration_missing，不要求用户理解SDK。
当前不变量：打开主页、普通导航、缺配置三方、打开本地协议均不调用wxApp/qq/短信/密码/captcha/refresh认证，不调用支付宝支付或猜测协议key，不新增Token/UserState/AccountStore写入；没有真实请求就没有HTTP loading。首页其他后台请求需从认证统计剔除。
后续真实流程：Idle→Authorizing→取消/拒绝/未安装/失败或合法凭据→Requesting→成功/失败→Idle。授权状态与真实HTTP loading分开；取消在凭据前不认证，失败不写Token，operationId忽略晚/重复回调，终态解除busy。不得用提供商普通主页或拼造deep link当授权。
主Agent已核实QQ新SDK给authCode，但本题后端要accessToken/openId，不可错传；微信参数不能猜，支付宝支付不能当登录。取得合法平台配置和后端交换契约后再闭合B9–B11，SDK声明/空配置边界存在不等于真实授权已通过。

## 6. 本地正文与需求映射

原创“青商城”用户协议/隐私政策各有实际段落、版本1.0/日期2026-10-20；记录原创路径与事实依据，分别Scroll可读到底、离线可读、返回可重进。覆盖服务/功能边界、账号认证、合法使用、联网/本地保存、权限与当前三方现状、用户实际可行管理方式。不虚构公司/联系方式、SDK集成、加密/固定期限、绝不共享、一键注销/删除能力或所有占位功能已上线。
事实核对：module声明INTERNET/MICROPHONE，EntryAbility启动确实请求录音，不能写不请求权限；登录页不依赖麦克风。UserState有持久化，AccountStore有密码存取能力但当前登录VM不调用，不能写默认保存所有密码。正文交需求角色复核，不能以长文字存在替代B14/B15内容验收。

| 原子项分组（完整41项） | 实施与验证 |
| --- | --- |
| A1；A2–A5；A6–A9；A10–A13；A14；A15 | 真实入口；应用Logo/顶部/中心/120；主按钮精确文案及实心圆角；次按钮文案及空心圆角；分别导航短信/账号真实目标 |
| B1–B2；B3–B5；B6–B8 | 提示文案/上下关系；3品牌图案/下方/等间距；3对应标签及下方位置 |
| B9；B10；B11 | 各provider可点、诚实缺配置/去重恢复可验证；真实授权仍保留未通过 |
| B12–B13；B14–B15；B16–B17；B18–B19 | 两真实页脚入口；原创对应正文与全文阅读；逐字同意文案/底部归属；两链接分别主题色 |
| C1；C2–C3；C4–C5；C6–C7 | 手机100%；MD70%居中；LG60%居中；三类窗口各自均匀图标间距及区域包含 |

## 7. 实施顺序、验证与回退

1. 先入口/目标页id与导航守卫，验证真实“我的”→双目标→返回可重进、无重复入栈；再完成Logo/按钮/三等宽列/精确文案/页脚滚动；再缺配置分支；最后两本地正文并需求复核。
2. 每个构建/设备命令的新PowerShell进程先加载`D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`，在本题根沿用baseline-notes的entry@default debug assembleHap命令；保存完整日志/退出码/产物hash，区分既有告警，不扫改无关代码。
3. 安装本次产物，真实启动→“我的”→登录取UI树/截图；测双目标/两协议全文及返回、三缺配置、连点、返回我的再进、冷启后入口、拒绝录音权限仍可操作。样式/品牌/Logo/主题色必须截图补证，id或编译通过不能证明视觉正确。
4. 真实手机/MD/LG窗口分别测比例/中心/图标间距/包含，记录px/vp/密度/安全区及page/content/region/Logo/icon边界；重点599/600与839/840vp，最多1物理像素舍入。测短高/横屏/resize/字体缩放，页脚可滚到。不注入假断点或缩放截图代替实际窗口；做不到的尺寸标未验证。
5. 认证零调用需动作隔离的调用/网络证据与静态链，不凭无loading宣称无HTTP；设备无抓包时如实记限制。操作前后登录态一致但不输出Token。必要单测只针对去重/缺配置不认证/恢复，不写复述布局的测试；验证脚本与证据留本题workflow/verification、logs、traces。
6. 比例错→只调LoginPage外框/安全区；短屏错→只调Scroll视口minHeight/伸缩布局；图标间距错→等宽列/同尺寸；连点/返回锁死→局部VM守卫；链接不可点→真实独立Text；正文事实错→只调正文资源并复审；未配置却请求/写Token/跳支付或普通主页→移除越界调用。若实现遵循本方案仍失败则回方案，违背契约则修实现。
7. D1–D5及12类边界沿用acceptance；输入/分页按有理由N/A，真实授权取消/回调/HTTP终态待合法接入后实测，不伪称当前已通过。未决仅U2合法身份/签名回调、凭据交换与真实设备账号条件；本轮未产生功能通过结论。

技术来源：本题源码/分析/需求复审为主。已读两ArkTS技能，knowledge-retriever检索脚本因打包缺references/doc_index.json失败，未作为成功检索/lint证据；类型/生命周期沿本题ObservedV2/Trace/BaseViewModel模式。后续公开SDK依据统一引用主Agent的本题provider-research记录及其官方链接，不使用来源工程。
