# cm-spec26 实现阶段结论（1-do）

交给 `2-submit.md` 使用。验收项编号见 `spec/acceptance.md`。

## 改动

- 新增 `feature/goods/src/main/ets/component/`：`GoodsCommentItem`（评价条目）、`GoodsCommentCard`（评价卡片）、`GoodsDetailTitle`（"商品详情"分隔标题）、`GoodsDetailImage`（详情图片）、`CommentImageViewer`（全屏查看器）。
- 新增 `feature/goods/src/main/ets/model/GoodsDetailImageDataSource.ets`：详情图 `LazyForEach` 数据源。
- 修改 `GoodsDetailPage.ets`：接入以上组件；查看器用 `bindContentCover` 挂在详情 List 上。
- 修改 `GoodsDetailViewModel.ets`：查看器状态（防重复打开）、评价/详情图读取与判空、请求成功后刷新数据源。
- 没有改模型、接口、路由、基线公共组件，没有新增请求。文案复用基线已有资源：`goods_reviews`、`goods_detail`、`anonymous_user`（goods 模块）、`modal_close`（"关闭"，ui 模块）。
- 稳定 id 按 acceptance 第 7 节全部补齐。

## 验证

- 构建：clean build 成功（`logs/clean.log`、`logs/build.log`）；带文件位置的 ArkTS 告警 234 条，位置集合与 `logs/baseline-build.log` 完全一致，没有新增。
- 安装：`logs/install.log`。
- 自测：`hypium_tests/test_goods_detail_comments.py` 共 17 条，最后一次全部通过（`logs/selftest.log`、`logs/selftest.json`）。`logs/reports/` 里保留了前两次失败的运行：第一次是 `harness.app.restart_app` 解析不到主 Ability，第二次是网络日志的计数解析写错了，两次都是测试脚本的问题，不是功能问题。
- 设备：本机模拟器 127.0.0.1:5555，arm64，API 23，1308×2880；数据源为公共服务 `mall.dusksnow.top`。

## 实现中发现的问题

- `bindContentCover` 的 builder 根节点如果直接是 `@ComponentV2` 自定义组件，组件创建后会立即收到 `aboutToDisappear`，内部 `@Local` 更新不再刷新（实测页码一直停在"1/2"）。改为外包一层 `Column` 后正常，代码注释里写明了原因。
- 查看器打开时按 Back 只关闭查看器，滚动位置保持（模拟器实测，A30）。

## 未覆盖 / 已知问题

- A9（昵称为空显示"匿名用户"）、A10（无评价不渲染评价卡）、A21（无 contentPics 不显示"商品详情"）：公共服务里没有这类数据，只做了代码审查，没有设备验证。
- A34（详情请求失败后重试）：没有在设备上模拟断网，未验证。基线的"重试"疑似点不动（baseline-notes 第 8 节第 3 条）属于已接受的残余风险（U8）。
- A19 加载背景：dump 只能看到占位节点存在、尺寸按 URL 的 w/h 比例计算（自测断言高度误差 ≤5%），背景色没有单独断言。
- 830026 这类 100 张详情图的商品没有在设备上滚到底；已用 `LazyForEach` 懒加载，44 张图的 830001 滚到底正常。
- 模拟器 DNS 偶发解析失败，自测会先 ping 等待；环境网络失败记为 skip，不算通过。
