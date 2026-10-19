# cmu-spec114 完成情况片段（供汇总进 `solution.md`）

## 1. 本题完成情况

- 状态：`submitted`。题目为“0.9.3 版本信息、应用内隐私页与搜索提示统一”（`spec/requirement.md`，三个场景）。
- 场景一（设置页 0.9.3）：`AppScope/app.json5` 改为 versionName `0.9.3` / versionCode `103`，`Constants.VERSION` 改为 `'0.9.3'`，设置页显示“0.9.3 - 测试版”；设置页其余内容未改。
- 场景二（应用内隐私页）：设置页“前往查看本软件的隐私政策”不再通过 `viewData` Want 打开外部浏览器，改为
  `router.pushUrl({ url: 'pages/PrivacyPage' }, router.RouterMode.Single)`；新增 `pages/PrivacyPage.ets`（标题栏“隐私政策” + `Web` 组件，加载基线原地址），
  在 `main_pages.json` 注册；返回不交给网页历史，一次返回回到设置页。
- 场景三（搜索提示）：`SearchComponent.ets` 的占位文案与空内容 Toast 共用常量“请输入搜索内容”，补充 `placeholderColor('#FF808080')`、`fontColor('#FF121212')`；
  判空时先 `trim()`，非空关键词仍按原值传给结果页。
- 构建与自测（均有日志，见 `tasks/cmu-spec114/logs/`）：
  - `hvigorw assembleHap` 构建成功（`logs/build.log`），无 ERROR；`entry/src` 的 ArkTS 告警由基线构建的 36 条变为 38 条，
    新增的是 `pushUrl` 与 `px2vp` 的 deprecated 告警（比对 `logs/baseline-build-clean.log`）。
  - 安装成功（`logs/install.log`）。自测 `hypium_tests/` 共 22 条（设置页 6、隐私页 9、搜索 7），全部通过（`logs/selftest.json`、`logs/selftest.log`，“Ran 22 tests … OK”）。
  - 自测在 Hypium + HarmonyOS 6.1.0 模拟器上运行，设备序列号 `127.0.0.1:5555`。

## 2. 未完成项

- 无已知的 Spec 场景未实现项。官方 F-point 的实际通过情况未知（正式测试脚本不公开，线上提交期间也没有官方反馈）。

## 3. 已知问题与未覆盖项

1. 隐私页正文为空白。会话 1611afd1 的排查（命令与输出见该会话消息 [1]、[3]）显示：Web 组件确实发出请求，随后报 `ERR_NAME_NOT_RESOLVED`；
   权威 DNS、阿里 DNS（223.5.5.5）、Google DNS（8.8.8.8）对 `docs.chenlvin.cc` 的 A/AAAA/CNAME 查询均返回 `NXDOMAIN`，同主域 `api.chenlvin.cc` 可解析。
   该会话据此判断是域名已失效而非模拟器网络问题，并且基线用外部浏览器打开同样空白。这个判断出自 AI 的会话输出，我只核对了其中命令输出的存在，没有自己重新做 DNS 查询。
   - 注意：`spec/acceptance.md` 第 7 节第 1 条仍写“本机模拟器上 DNS 无法解析（其它域名正常）”，是更早的说法，会话 1611afd1 消息 [3] 已指出该说法不准确并询问是否修改，
     此后用户没有要求修改，所以该文档至今未改。提交材料以本片段和会话记录为准；是否改写 `acceptance.md` 由队员决定（该文件在 `final.diff` 内，改动会使差异失效）。
   - 处理决定：沿用基线原地址（`spec/acceptance.md` 的 U4），不加本地页面兜底。标题“隐私政策”、Web 组件、留在本应用内、返回行为均已自测通过。
2. 刚进入设置页就立即按返回，约一半会被页面转场吞掉。设置页入口与返回逻辑本题未改动，推断为基线行为，**未用基线包复测**；自测在进入设置页后等待 1 秒。隐私页无此现象（连续 6 次零延迟返回成功）。
3. 占位色、输入文字色 Hypium 无法读取，只在浅色模式下看了截图（`logs/shots/`），深色模式未目检。
4. 非空搜索只验证到进入结果页；结果数据依赖后端服务，本地未接服务。
5. `build-profile.json5` 含 `"targetSdkVersion": "6.1.0(23)"`，来源疑为 DevEco 同步自动写入，已按用户决定保留，据 `spec/baseline-notes.md` 对产物无影响（会话 71bc8e00 用不含该改动的提交对照构建过，我未复核）。来源需队员确认。
6. 工程没有包含本题改动的 Git 提交，最终版本以“`bb23a62` + 工作区快照”标识（见 `trace-index.md`）。

## 4. AI 参与环节

- 需求分析与验收矩阵（会话 `71bc8e00-e056-404d-96d9-303160a3a9da`，0-analyze）：读取 Spec 与基线代码，产出 `spec/acceptance.md`（A/B/C/X 共 35 项验收、U1–U9 假设）与 `spec/baseline-notes.md`。
- 开发与自测（会话 `1611afd1-2e90-4647-ac14-b9bfc5fb0a02`，1-do）：实现三个场景、编写 `hypium_tests/`、构建安装、运行自测、排查隐私页空白。
- 两个会话末尾各有一轮只查询会话 ID 的对话，不属于研发环节。
- 使用的模型：`opus 5.5`（主要）、`gpt-6.1-sol`（仅 71bc8e00 的一个被中止的轮次）；详见 `trace-index.md`。
- 失败与重试：71bc8e00 有一次引擎重试后未正常结束的轮次、两次用户中止；原始记录均保留。

## 5. 人工协作与分工（本题部分）

- 团队成员及团队级分工见 `team.yaml`（赵琳慧：需求分析与方案设计；苏云鹤：AI 指导与代码编写；罗智文：测试与验收）。
  这是团队级分工，各成员在本题上的具体操作和对应会话没有任何记录可核实，本题级分工【待补充】。
- 本题中可从会话核实的人工参与：发起各阶段任务、对 U1–U9 假设“按推荐”的确认（71bc8e00 消息 [8]）、回复“1. 保留，2. 接受”（消息 [10]）、
  对隐私页空白的提问（1611afd1 消息 [2]、[4]）。
- 人工直接修改代码的情况：【待补充】，见 `trace-index.md`。

## 6. 本题记录索引

`tasks/cmu-spec114/trace-index.md`。
