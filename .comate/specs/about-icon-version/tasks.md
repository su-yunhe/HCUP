# 关于页展示圆形应用图标与动态版本号

- [✓] Task 1: 添加应用图标资源与常量
    - 1.1: 将 `AppScope/resources/base/media/foreground.png` 复制为 `commons/constants/src/main/resources/base/media/ic_app_icon.png`
    - 1.2: 在 `commons/constants/src/main/ets/Icon.ets` 新增 `ic_app_icon` 常量
    - 1.3: 在 `features/settings/src/main/resources/base/element/string.json` 新增 `app_icon_desc`（应用图标）

- [✓] Task 2: 改造 AboutPage 显示图标与版本号
    - 2.1: 新增 `@Local versionName` 状态，在 `aboutToAppear` 中用 `getBundleInfoForSelfSync(GET_BUNDLE_INFO_DEFAULT)` 读取 `versionName`，异常时 try/catch 记录 hilog
    - 2.2: 在 Scroll 内容顶部新增居中 Column：80vp 圆形 Image（borderRadius 40 + clip + 白底 + id + accessibilityText），下方 Text 显示纯 `versionName`（非空才渲染，带 id）
    - 2.3: 保留原有作者、简介、公众号、备案号内容与 Scroll/NavDestination 属性不变

- [✓] Task 3: 构建验证
    - 3.1: 执行 `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`
    - 3.2: 修复编译错误与新增 ArkTS 告警，直到构建成功

- [✓] Task 4: 编写并运行设备自测
    - 4.1: 新建 `hypium_tests/test_about_page.py`，按 test-harness 约定实现：首页→设置→关于路径导航
    - 4.2: 断言图标存在且宽高相等、版本文本等于 `bm dump` 读取的已安装 `versionName`、文本位于图标下方且水平居中
    - 4.3: 断言原有简介（GitHub/Gitee 仓库地址）、公众号、备案号内容仍在
    - 4.4: 返回设置页并重复进入 3 轮，验证显示一致、无崩溃
    - 4.5: 安装 HAP 到模拟器运行测试，截图确认圆形效果（浅色/深色模式）

- [✓] Task 5: 回归检查与收尾
    - 5.1: 检查 `git diff`，确认仅包含预期改动，未修改 `app.json5` 版本号
    - 5.2: 清理验证过程中产生的临时文件
