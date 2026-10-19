# 核心任务

在本工程中，按本工程 `spec/requirement.md` 的需求完成功能开发，目标是让尽可能多的官方 F-point 通过。

**前置**：必须先按 `0-analyze.md` 完成分析，拿到本工程 `spec/acceptance.md`（验收矩阵）和
`spec/baseline-notes.md`（基线理解结论）后再动手写代码。没有验收矩阵就直接改代码，等于放弃隐藏检查点。

本题基线提交号见本工程 `spec/metadata.json` 的 `base_commit`。

# 禁止事项（违反即废题）

以下是赛事章程第 5.6、5.7、5.8 条的硬红线，**违反会导致本题全部 F-point 不计通过，且仍计入分母**：

1. **不得访问本题来源项目（上游仓库）中与本题相关的任何内容**，包括：
   - 实现该功能的提交、合并请求、Issue、补丁，及其镜像、转载、副本
   - 上游仓库该功能相关文件的当前版本（main/master 分支上已实现的代码）
   - 上游仓库的提交历史、代码搜索结果、第三方转载的同功能代码
2. **不得访问题包目录**（`SWE-OpenHarmony/`）。本题所需资料已复制到本工程 `spec/`。
   题包里有其他赛题的 Spec 和基线，访问即违规。
3. **不得访问其他赛题的工程目录**（`harmonycup-work/` 下除本工程和 `common/` 之外的目录）。

允许访问的范围：

| 范围 | 用途 |
| --- | --- |
| 本工程目录 | 源码、`spec/`、`hypium_tests/`、`logs/` |
| `../common/`（相对本工程，即 `harmonycup-work/common/`） | 通用任务书 `spec-harness/`、测试框架 `test-harness/`、Python 环境 `.venv/`；**只读，不得修改** |
| 公开资料 | 鸿蒙官方文档、ArkTS/ArkUI API 资料、与本赛题无关的通用技术资料 |

检索到的页面若出现本应用的同功能实现，立即停止阅读并在产出中说明。

**不确定某个来源是否受保护时，不要访问，先问我。**

# 输入

| 文件 | 内容 |
| --- | --- |
| 本工程 `spec/requirement.md` | 本题需求说明 |
| 本工程 `spec/metadata.json` | `base_commit` 与基线 bundle 标识 |
| 本工程 `spec/acceptance.md` | 验收矩阵（由 `0-analyze.md` 产出） |
| 本工程 `spec/baseline-notes.md` | 基线理解结论（由 `0-analyze.md` 产出） |
| 工程源码 | 本题指定基线 |

需要去http://swe-openharmony.tech/#r-scoring 查看具体赛题技术答疑，看是否有本道题用得上的。

# 必做流程

按顺序执行，不要跳步。

1. **确认基线快照存在**。`0-analyze.md` 阶段应已打好标识；若没有，先 `git tag baseline-<题目ID>` 或记录 HEAD。
2. **走通端到端最短路径**，顺序固定：
   页面入口能进入 → 正常数据能展示 → 用户动作能触发 → 状态正确变化 →
   必要的网络请求或本地持久化真正发生 → 返回/重进/重启/重复操作正确 → 最后才做视觉细节。
3. **沿用基线既有结构**。若基线已有相近功能，优先复用其数据结构、状态管理和路由方式。
   官方测试会沿现有应用流程进入目标页面；另起一套页面或绕过原有服务，会导致入口、参数、返回栈对不上。
4. **涉及网络的需求显式设计状态机**，不要"先改 UI 再补请求"。
   隐藏测试可能直接观测网络行为，也可能快速重复点击验证是否产生重复请求。
5. **写 Hypium 自测脚本**到本工程 `hypium_tests/test_*.py`，测试类继承
   `common/test-harness` 中的 `harness.driver.HarnessTestCase`（框架用法见 `common/test-harness/README.md`）。
   为新增/关键组件设置稳定的 `.id()`，否则只能依赖脆弱的类型+顺序选择器。
6. **构建、安装本题 HAP，再跑自测**，全程留日志。命令均在本工程根目录执行：

   ```bash
   COMMON="$(cd ../common && pwd)"
   mkdir -p logs
   hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | tee logs/build.log
   hdc -t <设备序列号> install -r <本题HAP路径> 2>&1 | tee logs/install.log
   PROJ="$PWD"
   # 在 logs/ 下运行：Hypium 会在当前目录生成 reports/，避免污染工程根目录
   (cd logs && PYTHONPATH="$COMMON/test-harness" "$COMMON/.venv/bin/python" -m harness.runner \
       --project "$PROJ" --device <设备序列号> --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log)
   ```

   **每次跑自测前都必须先安装本题刚构建的 HAP。** 同一上游项目的多道题共用同一个 bundleName，
   模拟器上装的可能是别的题的构建产物，直接跑会测错对象。
   可用 `hdc shell "bm dump -n <bundleName>"` 的 `updateTime` 核对安装时间。
   需要 `hdc` 在 PATH 中（DevEco 的 `sdk/default/openharmony/toolchains`）。

7. **自测失败就修，修完重跑**，不要带着失败用例交付。
8. **交付前还原构建生成的噪声文件**（如各模块 `BuildProfile.ets` 因 `buildMode=debug` 被改写）：

  ```bash
  git checkout -- $(git diff --name-only | grep 'BuildProfile.ets')
  ```

# 开发时必须回答的验收维度

`spec/acceptance.md` 里的每一条都要落到代码和自测里。这些维度各自都可能是独立检查点：

| 维度 | 需要回答 |
| --- | --- |
| 入口 | 测试从哪个页面、哪个按钮或哪种初始状态开始？ |
| 前置数据 | 需要登录、地址、商品、歌曲、配置或服务端数据吗？ |
| 用户动作 | 测试会点击、滑动、输入、返回、重启还是重复操作？ |
| UI 结果 | 必须出现什么文字、组件、页面、状态或布局？ |
| 数据结果 | 是否要保存、删除、排序、追加、同步或持久化？ |
| 网络结果 | 是否必须真的发请求？请求何时发起？取消/关闭时是否不能发？ |
| 返回结果 | 返回后状态是否保持？滚动位置是否保持？ |
| 边界条件 | 空输入、纯空格、取消、重复点击、没有更多数据、部分操作如何处理？ |

文案必须与 Spec 完全一致，不要自行改写或美化。

# 完成标准

全部满足才算这一步完成，缺一项就继续改：

- [ ] `spec/acceptance.md` 中每条验收项都有对应实现
- [ ] 构建成功，无新增告警（与基线构建日志对比）
- [ ] 应用能安装、能冷启动、不崩溃
- [ ] `hypium_tests/` 自测全部通过，日志已存入 `logs/`
- [ ] 至少覆盖：首次进入、无数据、取消操作、返回后重进、重启应用、连续点击、空输入/纯空格
- [ ] 涉及网络的需求已确认请求真实发出，且取消/关闭时确实不发
- [ ] `git status` 只剩真实改动，无构建噪声文件
- [ ] 已知问题和未覆盖项已明确列出（交给 `2-submit.md` 用）

# 背景

本工程对应 2026 AI 辅助研发创新大赛（鸿蒙杯）的一道赛题。

评分单位是 F-point（从 Spec 归一化得到、可由 Hypium 执行判定的功能检查点）：

```
评测分 = 通过的 F-point 数 ÷ 本阶段全部 F-point 数 × 100
```

未提交、未完成、构建或安装失败、崩溃、超时、跳过、未执行的 F-point 都不计通过，**但仍计入分母**。
所以"没做"和"做崩了"扣分相同，而每道已做题目里多通过一个检查点都是净收益。

正式测试脚本、隐藏输入和参考答案都不公开，线上提交期间也没有官方反馈。
截止前多次提交以最后一次为准，不取历史最高分。因此自测体系是唯一可靠信号——
不要把"本地示例通过"或"界面看起来对了"当成完成。

Spec 中的场景数不等于官方 F-point 数量，可以用场景拆解开发和自测，但不要据此推断分值。

