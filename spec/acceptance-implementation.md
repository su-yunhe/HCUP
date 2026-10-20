# cml-spec24 验收实现索引

本文件补充分析阶段的 [原验收矩阵](D:/HCUP/cml-spec24/spec/acceptance.md)，保留原编号和原文。逐项结果、源码与安装指纹、实际命令和证据范围见 [最终验证报告](D:/HCUP/cml-spec24/workflow/verification/development-verification-v5.md) 和 [逐项结果](D:/HCUP/cml-spec24/workflow/verification/development-status-v5.json)。这些是本地拆解项，不是官方 F-point 数量或评分。

## 实现与测试映射

下表覆盖 A01–A76。N01–N12 是 [普通 Hypium 用例](D:/HCUP/cml-spec24/hypium_tests/test_goods_category_live.py) 的方法编号；C01–C09 是 [显式受控设备用例](D:/HCUP/cml-spec24/workflow/verification/test_controlled_ui_v1.py) 的方法编号。每一项的实际 case 目录和结果以逐项结果 JSON 为准。

| 验收项 | 实际实现 | 主要自测 |
| --- | --- | --- |
| A01–A05 | [首页入口](D:/HCUP/cml-spec24/feature/main/src/main/ets/view/HomePage.ets)、[分类入口](D:/HCUP/cml-spec24/feature/main/src/main/ets/view/CategoryPage.ets)、[搜索导航](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsSearchViewModel.ets)、[目标页初始化](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:73) | N01、N02、N03、N07 |
| A06–A15 | [搜索栏、控制栏与双布局](D:/HCUP/cml-spec24/feature/goods/src/main/ets/view/GoodsCategoryPage.ets:78)、[网格卡](D:/HCUP/cml-spec24/core/ui/src/main/ets/component/goods/GoodsGridItem.ets)、[列表卡](D:/HCUP/cml-spec24/core/ui/src/main/ets/component/goods/GoodsListItem.ets) | N01、N06；实际可见卡审计 |
| A16–A18 | [分页和刷新入口](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:178)、[原生 Refresh 与 Grid/List](D:/HCUP/cml-spec24/feature/goods/src/main/ets/view/GoodsCategoryPage.ets:103) | N06；C02、C03、C08 |
| A19–A37 | [筛选面板](D:/HCUP/cml-spec24/feature/goods/src/main/ets/view/GoodsCategoryPage.ets:182)、[草稿与统一确认](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:140) | N05、N08、N09、N10、N12；C04、C09 |
| A38–A52 | [排序菜单](D:/HCUP/cml-spec24/feature/goods/src/main/ets/view/GoodsCategoryPage.ets:239)、[排序应用](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:166) | N04、N11、N12 |
| A53–A61 | [完整查询快照](D:/HCUP/cml-spec24/feature/goods/src/main/ets/model/GoodsCategoryState.ets)、[请求版本、提交页码与终态](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:214) | N03、N06、N11、N12；C01、C02、C03、C05、C06、C08；原代码 host14 |
| A62–A64 | [失败分支与生命周期隔离](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:403)、[错误、空态及真实操作按钮](D:/HCUP/cml-spec24/feature/goods/src/main/ets/view/GoodsCategoryPage.ets:103) | N07；C01、C02、C03、C04、C05、C07 |
| A65–A66 | [排序菜单关闭和标题](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:166) | N04 |
| A67–A74 | [搜索、价格校验、草稿重置与关闭](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets)、[已裁决边界](D:/HCUP/cml-spec24/workflow/requirements/development-review-v2.md) | N03、N05、N08、N09、N10、N12；C04、C09；服务契约取证 |
| A75 | [每个目的页独立 VM 与生命周期](D:/HCUP/cml-spec24/feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:73)、[既有导航包装](D:/HCUP/cml-spec24/core/ui/src/main/ets/component/navdestination/AppNavDestination.ets) | N07；C07 |
| A76 | 沿用 [GoodsRepository](D:/HCUP/cml-spec24/core/data/src/main/ets/repository/GoodsRepository.ets) 和 [RequestHelper](D:/HCUP/cml-spec24/core/result/src/main/ets/RequestHelper.ets)，由 VM 构建实际服务参数 | 正常 App 实际请求/响应片段、独立即时服务 oracle、服务契约取证、host14 |

## 证据解释

- 普通 N 用例运行最终正常 HAP，使用既有真实服务。App 原始不完整响应保留原状，独立 oracle 单独存储；不将重放结果伪装成 App 原响应。
- C 用例在独立 ohosTest 模块运行同一原 Page、VM、Repository、RequestHelper，仅控制外部 DataSource Promise。它证明实际 ArkUI 状态与真实导航行为，不代表生产服务物理断网、HTTP 超时或服务器乱序实测。
- C01–C06 与 C07–C09 的有效结果来自同一冻结源码及同一 HAP 的两轮组合。原首轮 C07 测试宿主输入前置失败和非零退出保留，不能写作单轮九例退出 0。
- 价格端点沿实测服务的 `(min,max]`；重置清除可编辑分类和价格，保留关键词、显式 `featured`/`recommend` 与排序。完整工程决议见需求复审记录，不把这些未写明的语义冒称为 Spec 原句。
- 运行设备为本题独立 x86_64 模拟器。default HAP 保留原 arm64 库，arm64 真机及未涉及的原生能力未实测；官方隐藏测试不可见。
