import { GoodsRepository } from "data";
import { GoodsCategoryParam } from "navigation";
import GoodsCategoryViewModel from "goods/src/main/ets/viewmodel/GoodsCategoryViewModel";
import { ControlledGoodsDataSource } from "./ControlledGoodsDataSource";
import { FixtureRequestQueue } from "./FixtureProtocol";

export class FixtureRouteParam implements GoodsCategoryParam {
  instanceId: number;
  keyword?: string;
  typeId?: string;
  featured?: boolean;
  recommend?: boolean;
  minPrice?: string;
  constructor(instanceId: number, keyword: string, scenario: string) {
    this.instanceId = instanceId;
    this.keyword = keyword.trim().length > 0 ? keyword.trim() : undefined;
    this.typeId = scenario === "root" ? "900001" : undefined;
    if (scenario === "flags") {
      this.keyword = this.keyword ?? "X";
      this.typeId = "920001";
      this.featured = false;
      this.recommend = true;
      this.minPrice = "50";
    }
  }
}

class FixtureSession {
  vm: GoodsCategoryViewModel;
  constructor(vm: GoodsCategoryViewModel) { this.vm = vm; }
}

/** Owns stable instances and actual Navigation actions; no direct VM state manipulation. */
@ObservedV2
export class FixtureController {
  readonly stack: NavPathStack = new NavPathStack();
  readonly queue: FixtureRequestQueue = new FixtureRequestQueue();
  @Trace scenario: string = "manual";
  @Trace keyword: string = "";
  @Trace result: string = "normal";
  @Trace requestId: string = "";
  @Trace currentInstance: number = 0;
  private sessions: Map<number, FixtureSession> = new Map();
  private instanceSequence: number = 0;

  reset(): void {
    this.stack.clear(false);
    this.queue.note("nav clear");
    this.open();
  }

  open(): void {
    const scenario: string = this.scenario.trim();
    if (!["manual", "root", "empty", "fullEnd", "missingMeta", "flags"].includes(scenario)) {
      this.queue.note(`invalid scenario ${scenario}`);
      return;
    }
    const instanceId: number = ++this.instanceSequence;
    const dataSource: ControlledGoodsDataSource = new ControlledGoodsDataSource(this.queue, instanceId, scenario);
    this.sessions.set(instanceId, new FixtureSession(new GoodsCategoryViewModel(new GoodsRepository(dataSource))));
    this.currentInstance = instanceId;
    const param: FixtureRouteParam = new FixtureRouteParam(instanceId, this.keyword, scenario);
    this.stack.pushPath({ name: `gcf.goods.${instanceId}`, param: param }, false);
    this.queue.note(`nav open instance=${instanceId} scenario=${scenario}`);
  }

  vmFor(instanceId: number): GoodsCategoryViewModel {
    const session: FixtureSession | undefined = this.sessions.get(instanceId);
    if (session === undefined) { throw new Error(`missing fixture instance ${instanceId}`); }
    return session.vm;
  }

  cover(): void {
    this.stack.pushPath({ name: "gcf.cover" }, false);
    this.queue.note("nav cover");
  }

  back(): void {
    this.stack.pop(false);
    this.queue.note("nav pop");
  }

  resolve(): void {
    if (!["normal", "empty", "business", "missingMeta", "wrongPage"].includes(this.result.trim())) {
      this.queue.note(`invalid result ${this.result}`);
      return;
    }
    this.queue.resolve(Number(this.requestId.trim()), this.result.trim());
  }

  reject(): void { this.queue.reject(Number(this.requestId.trim())); }
}
