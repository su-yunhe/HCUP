# cml-spec1 提交工程事实审计 r1

审计日期：2026-10-20。角色：`/root/submission_implementation`。本轮仅写本报告，未修改生产代码、资源、配置、测试、其他角色报告或调度状态；未重新构建，未执行设备命令。结论仅用于主 Agent 整理提交材料，不代替独立验收或官方隐藏测试。

## 1. 应用与构建事实

| 事实 | 核实值 | 证据 |
| --- | --- | --- |
| 官方基线 / 当前 HEAD | `7014cebd60f2181fac2a36d399ca16b3d6a175ab`，两者相同；功能修改仍在工作区 | `spec/metadata.json`；本轮 `git rev-parse HEAD` |
| 基线 bundle 声明 | `repo_bundles/coolmallarkts-7014cebd60-base.bundle` | `spec/metadata.json`；仅引用元数据，未访问该路径 |
| bundleName | `com.joker.coolmall` | `AppScope/app.json5`；产物 `entry/build/default/outputs/default/pack.info` |
| 模块 / 主入口 | `entry` / `EntryAbility`，`mainElement=EntryAbility` | `entry/src/main/module.json5`；上述 pack.info |
| 入口源码 | `entry/src/main/ets/entryability/EntryAbility.ets` | module.json5 的 `srcEntry` |
| 应用版本 | `versionCode=1000000`，`versionName=1.0.0` | AppScope/app.json5；pack.info |
| 工程目标 | `default` product，HarmonyOS，target/compatible `6.0.1(21)`，debug/release | `build-profile.json5`；pack.info 的 API21 |
| 实际使用工具 | DevEco 6.1.0.860 / SDK API23；Node 18.20.1、JBR 21.0.8、hdc 3.2.0c | `logs/analysis-baseline-env.json`；`logs/verification-do-build-run-r2-{node,java,hdc}-version.log`；`workflow/verification/do-result-r4.md` |
| 签名状态 | `signingConfigs: []`，最终 HAP 为 unsigned；原始构建保留 No signingConfig 告警 | build-profile.json5；`logs/verification-do-build-run-r2-assembleHap.log` |

工程配置的 API21 与本机实际 SDK API23 是两个不同字段，提交说明不得互相替换。未签名 HAP 在本题模拟器安装成功有原始记录，其他设备的签名/安装条件本轮未验证。

## 2. 官方准备及依赖

- `logs/prepare-baseline.log` 是实际保留的 JSON 输出：`profile=harmony-cup-build-v1`、`task_id=cml-spec1`、`dry_run=false`、正确 base_commit、`changes=[]`。`workflow/setup-result.json` 将该步骤记为 pass，未改变业务或准备配置。
- 任务要求的 `D:/SWE-OpenHarmony/reports/build-baselines/cml-spec1.log` 本轮实际读取失败：文件不存在。没有跨授权目录寻找替代品。上述本题日志可证明本地准备输出，但不能冒称为缺失的题包 reports 原文；该来源缺口应在材料中披露。
- 根 `oh-package.json5` / `oh-package-lock.json5` 为 modelVersion 6.0.1、锁文件版本3，开发依赖 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`。entry 依赖工程内 `file:` 相对路径模块，须随完整工程提交。
- 本题新增运行依赖仅 `feature/main/oh-package.json5` 的 `@ohos/lottie=2.0.33`。`feature/main/oh-package-lock.json5` 和 `entry/oh-package-lock.json5` 都新增同一包及 integrity，resolved 为 `https://ohpm.openharmony.cn/ohpm/@ohos/lottie/-/lottie-2.0.33.har`，属于必要依赖记录，应保留在 diff。
- `logs/ohpm-install.log` 保留 `@hview/dayjs` 下载 ETIMEDOUT 后成功下载、最终 install completed；`logs/ohpm-install-exit-code.txt` 为0。`logs/do-ohpm-install-r1.log` 保留真实 Lottie 元数据及 HAR 获取成功。失败/重试行不能删去。

## 3. 可携带的构建和运行命令

以下是由原始 argv 改写为工程内相对路径的说明命令，本轮没有执行。前置：在工程根目录，用复现方安装的 DevEco/SDK 设置 `JAVA_HOME`、`DEVECO_SDK_HOME` 及 PATH，使 `node`、`java`、`ohpm`、`hvigorw`、`hdc` 可用。根目录没有随仓库提供 hvigorw 包装脚本，`hvigorw` 来自 DevEco 工具。提交说明不能把本机的绝对安装路径或环境激活脚本当作必需的未提交文件。

```powershell
ohpm install --all
hvigorw clean --mode module -p product=default -p buildMode=debug --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
hdc list targets
# 将目标序列号填入变量；本题原始实测值为 127.0.0.1:11245。
$taskDevice = '<设备序列号>'
hdc -t $taskDevice install -r ./entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $taskDevice shell bm dump -n com.joker.coolmall
hdc -t $taskDevice shell aa start -a EntryAbility -b com.joker.coolmall
```

真实命令来源：`logs/do-build-r1-result.json`（ohpm install --all / assembleApp）、`logs/verification-do-build-run-r1-commands.json`（clean + assembleHap）、`logs/verification-do-build-run-r2-commands.json`（最终冻结后 assembleHap）、`logs/verification-do-run-run-r4-commands.json`（安装与 bm dump）、`logs/analysis-baseline-r3-launch-first.json`（aa start）。首次启动配置、路由及数据库初始化仍由 EntryAbility 保留逻辑执行，未发现需人工写入账号/数据库才能进入本题主页面的已批准步骤。

历史执行辅助 `traces/verification-do-r1/run-frozen.ps1` 固定本地环境脚本和专用设备，还含当时的冻结授权门禁；它是执行证据，不适合作为通用复现入口。其 PowerShell 构建进程确实加载本题环境覆盖脚本；携带说明应保留上述标准 argv 并单独说明复现方工具环境。

## 4. 最终产物与日志绑定

| 项目 | 值 / 证据 |
| --- | --- |
| 最终 HAP | `entry/build/default/outputs/default/entry-default-unsigned.hap` |
| 本轮实算大小 | **20,739,960 bytes** |
| 本轮实算 SHA-256 | `d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615` |
| 最后生产修复构建 | `logs/do-build-r3-debug.log` / `logs/do-build-r3-result.json`；13:00:37–13:00:53 +08:00，exit0 |
| 独立最终构建 | `logs/verification-do-build-run-r2-commands.json` / `logs/verification-do-build-run-r2-assembleHap.log`；13:02:18–13:02:24 +08:00，exit0，BUILD SUCCESSFUL in 4 s 351 ms |
| 缓存事实 | 最终独立构建大量 UP-TO-DATE，包括 PackageHap；不得写成最终版本又做了一次 clean 全量编译 |
| 独立首次全量构建 | `logs/verification-do-build-run-r1-clean.log` / `logs/verification-do-build-run-r1-assembleHap.log`，clean/assemble 均 exit0，针对修复前 r1 冻结 |
| 原有告警 | `traces/verification-do-r1/independent-warning-compare-r1.json`：182 条带文件诊断，新增/删除均空；最终增量日志不代表重新输出182条 |
| 安装确认 | `logs/verification-do-run-run-r4-install-current-hap.log` 明确 install bundle successfully；commands.json 记录 exit0 |
| 独立结束核验 | `traces/verification-do-r1/run-r4/final-audit.json` 与 `workflow/do-delivery-validation.json`：HAP、688文件及测试脚本绑定一致 |

本轮读取实际 HAP 并计算摘要，与冻结清单及上述独立结束核验一致。`logs/selftest-run-r4.json` 记录8个 case 全 pass；具体动态断言及历史失败归因引用独立角色的 `workflow/verification/do-result-r4.md`，本审计没有重做设备验收。历史生命周期超时及截图重试应继续保留其原始日志，不用本轮静态审计抹去。

## 5. Git 真实改动与构建噪声

本轮 `git diff --stat` 为11个 tracked 文件、329 insertions / 249 deletions，无 tracked 删除、新增或二进制修改；另有11个新增生产文件，合计22个生产改动。

| 分类 | 文件 |
| --- | --- |
| 启动逻辑 | `entry/src/main/ets/entryability/EntryAbility.ets` |
| 必要依赖 | `entry/oh-package-lock.json5`、`feature/main/oh-package-lock.json5`、`feature/main/oh-package.json5` |
| 五个主页面 | `feature/main/src/main/ets/view/{CartPage,CategoryPage,HomePage,MainPage,MePage}.ets` |
| 状态/内容模型 | `feature/main/src/main/ets/viewmodel/{HomeViewModel,MainViewModel}.ets` |
| 新组件 | `feature/main/src/main/ets/component/TabLottieIcon.ets` |
| 新文本资源 | rawfile/lottie 下4个 JSON、rawfile/products 下6个 SVG，详见下一节 |

`git diff --name-only -- '*BuildProfile.ets'` 和 `git ls-files -- '*BuildProfile.ets'` 均空；`.gitignore` 已忽略 `**/BuildProfile.ets`、`**/build`、oh_modules、.hvigor 等。本轮 `git diff --check` exit0，仅既有 autocrlf 提示。没有待还原的 tracked 构建噪声，未执行还原操作。锁文件虽然自动生成，但这里准确记录新增运行依赖，不能当作构建噪声删掉。

普通 `git diff base_commit` 不覆盖未跟踪文件；仅交生产 patch 将遗漏 spec、测试、配置、工作流和轨迹。最终完整 diff 必须从确定的完整工程快照生成，并与该快照逐文件核对。

## 6. 资源与二进制

对基线当前允许的677个 blob 做只读 SHA-256 比对；基线含14个 Git 判定二进制（前8000字节含 NUL）。22个生产改动均无 NUL，新增资源为 JSON/SVG 文本，无新增/修改的生产二进制资源。以下10个新增资源与基线677个 blob 均无逐字节相同项；这只说明没有完全相同的基线副本，不证明创作来源。自制来源声明应引用 `workflow/implementation/do-handoff-r1.md` 及当时原生实现轨迹，不能仅靠本次哈希推定。

所有路径以下列公共前缀为根：`feature/main/src/main/resources/rawfile/`。

| 路径后缀 | bytes | SHA-256 |
| --- | ---: | --- |
| `lottie/tab_cart.json` | 2171 | `218a2c9fdcb91c18cacd844e59ad672a9d9e1f913ea597d990723dc9e2199624` |
| `lottie/tab_category.json` | 2225 | `07a7fa56f220fda045ab910a18fc1bc3d3fce772dac9c404c2bdf464845b568f` |
| `lottie/tab_home.json` | 2262 | `8e18829ecb6ade7c97429467ccd605b81cb1cf2f4791f86e152dcba8cc6edb3a` |
| `lottie/tab_me.json` | 2101 | `92ef8cf34d2ba5f4e5a2539282391ea946bc646b00ce5d162ed552402d7c6f90` |
| `products/bag.svg` | 347 | `201e059894a84b02e81e3d203d2bca136c0da95aa7a36d4b34b2d0438f3b06f4` |
| `products/kettle.svg` | 479 | `b5431742eb73c01ddbb602647f8fb3eb570ebe473a18dde24113a1e29baca198` |
| `products/lamp.svg` | 364 | `e31ed191039b0c50d5da043c1344d31d85f4e90c20a2aa2448952c1823d79c3f` |
| `products/mug.svg` | 479 | `ff54b3620aabeefa3416e182de754d80704c26bc32e8ffc32637109badb98048` |
| `products/speaker.svg` | 407 | `d7a59a820fb7cf89a501de92f3759180645f641f874dd43b5e12e821d0598a51` |
| `products/vase.svg` | 497 | `767df3115538b4abac9413d5b6d2531a7bbc669ba0d65e12344ffdc0fab95eaf` |

完整工作区还含大量过程二进制（截图、多帧JPEG、压缩日志、模拟器镜像及 pyc），不等于业务资源。本轮枚举时 traces 为10,894个未跟踪文件、2,361,262,811 bytes，其中 `traces/baseline-analysis/emulator-instances/CmlSpec1Baseline/userdata.img.qcow2` 1,473,380,352 bytes，`cache.img` 69,206,016 bytes；这些数字是当时的只读枚举，过程材料仍在生成，不是提交冻结值。保留的截图/失败压缩日志需要由最终快照清单逐个列大小与 SHA-256，不能用本节“生产二进制为0”替代完整材料二进制清单。

## 7. 两种快照必须分开

### 已核验的生产冻结 r2

- 清单：`traces/do-implementation/source-frozen-r2.json`。
- 清单文件 SHA-256：`d78e4b4781f4dd45cf1467d4a90fa4111e06b796ba31acaebe3be93e481ee882`。
- 688文件聚合 SHA-256：`2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c`。
- 算法：文件 path→SHA-256 map，JSON `ensure_ascii=False, sort_keys=True, separators=(',', ':')` 后对 UTF-8 bytes 再 SHA-256。
- 本轮实算：688文件零变化，清单集合与 `677 tracked + 11 untracked feature/main` 完全一致，聚合及 HAP 均一致。
- 范围解释须准确：全部 tracked 中实际包括115个基线 `src/test/` 或 `src/ohosTest/` 文件；它排除的是新增 hypium_tests 及过程材料，不能泛称“排除所有测试”。

### 完整项目提交快照

主 Agent 本轮已指定建议唯一工程源为 `.comate/submission-draft/traces/code-snapshot/project`。边界是保留源码、资源、配置及 spec/hypium_tests/system-config/workflow/traces、ignored AGENTS.md；排除 .git、构建/依赖/__pycache__、submission-draft本身、运行时 `*.img`/`*.qcow2` 和初始化混合会话目录 `traces/native/20261020T031347Z-6162c371`。保留全部相关失败日志。

该完整快照需在材料停止写入后冻结，另给文件清单与总体指纹；最终 `changes/final.diff` 必须与其逐文件hash比对，并从 base_commit 执行 `git apply --check --binary` 与应用后比对。生产 r2 指纹不能代替该检查。本角色未获派生成或校验完整快照/patch，本报告不声明这些步骤已通过。

## 8. 审计方法、缺口及交还

已完成：配置/产物交叉核实，原始依赖和构建/设备 argv 审阅，当前 git 状态与噪声检查，生产冻结与 HAP 实算，新增资源对基线对象的逐字节同源检查。只读对象访问限于本工程当前状态与指定 base_commit，没有查询来源上游历史、修复、Issue、PR、补丁或其他题工程。

审计范围失误如实披露：识别未跟踪二进制的脚本对 `git ls-files --others --exclude-standard` 的文件前8000字节做 NUL 检测，未预先排除初始化混合会话目录，因此不能声称该次前缀扫描未触及该目录。脚本没有解析、输出或引用会话文本，未将其作为实现参考或功能开发证据；后续停止此类全范围内容扫描，已向主 Agent 报告。按任务要求，本轮未阅读初始化总览会话内容用于实现或判断来源。

需主 Agent 收口：缺失的官方 reports 原文披露；完整项目快照、二进制清单及完整可应用 diff 的独立校验；最终材料冻结时再次确认生产聚合/HAP未变。报告中的携带命令没有重新执行验证；它们有实际 argv、退出码与原始日志支持。最终完成结论由主 Agent 结合独立自测与材料验证作出。
