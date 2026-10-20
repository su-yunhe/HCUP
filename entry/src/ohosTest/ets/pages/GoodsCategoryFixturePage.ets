import { GoodsCategoryPage } from "goods/src/main/ets/view/GoodsCategoryPage";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { setNavPathStack } from "navigation";
import { getHostCtx } from "util";
import EntryViewModel from "../../../main/ets/viewmodel/EntryViewModel";
import { FixtureController, FixtureRouteParam } from "../fixture/FixtureController";
import { FixtureRequestRecord } from "../fixture/FixtureProtocol";

@Entry
@ComponentV2
struct GoodsCategoryFixturePage {
  @Local private controller: FixtureController = new FixtureController();
  @Local private safeArea: WindowSafeAreaState = getWindowSafeAreaState();
  private windowVm: EntryViewModel = new EntryViewModel();

  aboutToAppear(): void {
    const context = getHostCtx(this);
    if (context !== undefined) { this.windowVm.aboutToAppear(context); }
    setNavPathStack(this.controller.stack);
  }

  aboutToDisappear(): void { this.windowVm.aboutToDisappear(); }

  @Builder
  private Destination(name: string, param: Object): void {
    if (name === "gcf.cover") {
      NavDestination() {
        Column({ space: 16 }) {
          Text("夹具覆盖页").id("gcf.cover.page");
          Button("返回原实例").id("gcf.cover.back").onClick((): void => this.controller.back());
        }.width("100%").height("100%").justifyContent(FlexAlign.Center);
      }.hideTitleBar(true)
      .onShown((): void => this.controller.queue.note("cover shown"))
      .onHidden((): void => this.controller.queue.note("cover hidden"));
    } else {
      GoodsCategoryPage({ vm: this.controller.vmFor((param as FixtureRouteParam).instanceId) });
    }
  }

  build(): void {
    Column() {
      this.ControlPanel();
      Navigation(this.controller.stack) {
        Column({ space: 12 }) {
          Text("请选择场景并打开原商品页").id("gcf.host.ready");
          Button("打开实例").onClick((): void => this.controller.open());
        }.width("100%").height("100%").justifyContent(FlexAlign.Center);
      }.id("gcf.navigation").hideTitleBar(true).mode(NavigationMode.Stack)
      .navDestination(this.Destination).layoutWeight(1).width("100%");
    }.width("100%").height("100%").backgroundColor(Color.White);
  }

  @Builder
  private ControlPanel(): void {
    Column({ space: 4 }) {
      Row({ space: 4 }) {
        TextInput({ text: this.controller.scenario, placeholder: "manual/root/empty/fullEnd/missingMeta" })
          .id("gcf.control.scenario").height(32).layoutWeight(2)
          .onChange((value: string): void => { this.controller.scenario = value; });
        TextInput({ text: this.controller.keyword, placeholder: "入口keyword" })
          .id("gcf.control.keyword").height(32).layoutWeight(1)
          .onChange((value: string): void => { this.controller.keyword = value; });
        Button("重建").id("gcf.control.reset").fontSize(12).height(30)
          .onClick((): void => this.controller.reset());
      }.width("100%");
      Row({ space: 4 }) {
        TextInput({ text: this.controller.requestId, placeholder: "请求ID" })
          .id("gcf.control.requestId").height(32).layoutWeight(1)
          .onChange((value: string): void => { this.controller.requestId = value; });
        TextInput({ text: this.controller.result, placeholder: "normal/empty/business/missingMeta" })
          .id("gcf.control.result").height(32).layoutWeight(2)
          .onChange((value: string): void => { this.controller.result = value; });
        Button("释放").id("gcf.control.resolve").height(30).fontSize(12)
          .onClick((): void => this.controller.resolve());
        Button("拒绝").id("gcf.control.reject").height(30).fontSize(12)
          .onClick((): void => this.controller.reject());
      }.width("100%");
      Row({ space: 6 }) {
        Button("新实例").id("gcf.nav.open").height(28).fontSize(12)
          .onClick((): void => this.controller.open());
        Button("覆盖").id("gcf.nav.cover").height(28).fontSize(12)
          .onClick((): void => this.controller.cover());
        Button("弹栈").id("gcf.nav.back").height(28).fontSize(12)
          .onClick((): void => this.controller.back());
        Text(`${this.controller.scenario} instance=${this.controller.currentInstance}`)
          .id("gcf.status.scenario").fontSize(10).layoutWeight(1);
      }.width("100%");
      Row({ space: 8 }) {
        Text(`pending=${this.controller.queue.pending.map((record: FixtureRequestRecord): number => record.id).join(",")}`)
          .id("gcf.status.pending").fontSize(10).layoutWeight(1);
        Text(`${this.controller.queue.eventSeq}`).id("gcf.status.eventSeq").fontSize(10);
      }.width("100%");
      Text(this.controller.queue.lastEvent).id("gcf.status.lastEvent").fontSize(10).width("100%").maxLines(1);
      Scroll() {
        Column({ space: 2 }) {
          ForEach(this.controller.queue.pending, (record: FixtureRequestRecord): void => {
            Text(JSON.stringify(record)).id(`gcf.pending.${record.id}`).fontSize(10).width("100%");
          }, (record: FixtureRequestRecord): string => `${record.id}`);
        }.width("100%");
      }.id("gcf.pending.scroll").height(48).width("100%");
    }.id("gcf.controls").width("100%")
    .padding({ top: this.safeArea.topInset, left: 6, right: 6, bottom: 4 })
    .backgroundColor("#EEEEEE");
  }
}
