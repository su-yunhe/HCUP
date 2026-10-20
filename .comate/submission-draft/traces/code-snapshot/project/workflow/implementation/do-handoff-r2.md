# cml-spec1 局部修复交接 r2

本轮仅接受主 Agent 派工修复独立自测确认的 A4 失败。设备已由测试角色停止并交还；本角色未操作设备，未修改需求、设计、测试、断言、验证记录或调度状态。r1 交接及全部历史日志保留。

## 失败证据与最小修复

已核对 `traces/verification-do-r1/repro-tab-reset-r1/commands.json`、`before-summary.json`、`after-summary.json` 及源码前后指纹：正常启动后仅一次原生分类 click；同一个 MainPage 实例从 index=0/epoch=1 变为 index=0/epoch=3，复现了切分类后意外回首页；复现期间源码 before/after 完全一致。

批准根因是 Swiper 的常量 `.index(0)` 在 VM/accessibilityDescription 更新时回写首页。唯一生产修改：

- `feature/main/src/main/ets/view/MainPage.ets:84`：`.index(0)` → `.index(this.vm.selectedIndex)`。

保留 controller 请求、仅 Swiper.onChange 调用 commitSelection、相同索引去重和所有原入口/动画/滚动行为。直接修复 A4 的选择稳定性，同时影响 A5–A22、A29–A30、A33 等后续依赖切页的一致性；其余 A1–A44 实现映射沿用 r1，不声称设备回归通过。

## 局部检查

- 按原 ArkTS/checker 配置，以真实 hvigor 编译诊断；每个构建 PowerShell 进程先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。
- 本轮仅一次必要 debug 构建：`hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`。
- 起止：2026-10-20T13:00:37.1511443+08:00 – 2026-10-20T13:00:53.7762745+08:00；exit=0；BUILD SUCCESSFUL in 14 s 162 ms。
- 日志：`logs/do-build-r3-debug.log`、`logs/do-build-r3-result.json`；没有安装、启动或设备功能检查。
- 带文件告警：基线 182，本轮 182；新增/删除均为空，见 `traces/do-implementation/debug-warning-compare-r2.json`。没有抑制、删除或改写原有告警。
- `git diff --check` 无错误，`logs/do-diff-check-r2.log`；仅原 autocrlf 提示。tracked diff 没有 BuildProfile.ets 噪声，无需还原。
- 688 个生产输入与 r1 比较仅上述 MainPage 一个文件哈希改变，见 `traces/do-implementation/repair-delta-r2.json`；没有全面重构。

## 新指纹与重新冻结

**局部修复完成，生产代码已重新冻结；独立自测运行期间禁止编辑源码。**

- 新源码完整指纹：`traces/do-implementation/source-frozen-r2.json`，688 输入；聚合 SHA256=`2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c`。算法和范围与 r1 完全一致。
- MainPage SHA256=`3966353ef151a360d6a69359a5b877a57038de9d0b025747553efcfa8ec05c13`。
- 本轮 HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，20,739,960 bytes，SHA256=`d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615`。
- 可重跑证据脚本：`traces/do-implementation/freeze-r2.py`。
- 未解决项：修复是否消除单次分类点击回首页，以及其他 8 流程的动态回归，均待独立角色重新构建、安装、实测。构建成功不代替 A4 或其他功能验收结论。
