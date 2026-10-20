import { GoodsSearchRequest, NetworkResponse } from "model";

export class FixtureRequestRecord {
  id: number;
  instanceId: number;
  scenario: string;
  kind: string;
  request?: GoodsSearchRequest;
  state: string = "pending";
  startedAt: number = Date.now();
  completedAt?: number;
  responseJson?: string;
  responseIds: number[] = [];
  responseCode?: number;
  error?: string;

  constructor(id: number, instanceId: number, scenario: string, kind: string, request?: GoodsSearchRequest) {
    this.id = id;
    this.instanceId = instanceId;
    this.scenario = scenario;
    this.kind = kind;
    if (request !== undefined) {
      this.request = new GoodsSearchRequest(request);
      this.request.typeId = request.typeId?.slice();
    }
  }
}

class FixtureAuditEvent {
  seq: number;
  event: string;
  id: number;
  owner: number;
  scenario: string;
  kind: string;
  request?: GoodsSearchRequest;
  ids: number[];
  code?: number;
  error?: string;
  at: number = Date.now();
  constructor(seq: number, event: string, record: FixtureRequestRecord) {
    this.seq = seq; this.event = event; this.id = record.id; this.owner = record.instanceId;
    this.scenario = record.scenario; this.kind = record.kind; this.request = record.request;
    this.ids = record.responseIds.slice(); this.code = record.responseCode; this.error = record.error;
  }
}

class FixturePendingOperation {
  resolve: (result: string) => void;
  reject: () => void;
  constructor(resolve: (result: string) => void, reject: () => void) {
    this.resolve = resolve;
    this.reject = reject;
  }
}

/** External IO control only: does not access a ViewModel or implement paging state. */
@ObservedV2
export class FixtureRequestQueue {
  @Trace records: FixtureRequestRecord[] = [];
  @Trace eventSeq: number = 0;
  @Trace lastEvent: string = "idle";
  private sequence: number = 0;
  private operations: Map<number, FixturePendingOperation> = new Map();

  get pending(): FixtureRequestRecord[] {
    return this.records.filter((record: FixtureRequestRecord): boolean => record.state === "pending");
  }

  enqueue<T>(instanceId: number, scenario: string, kind: string, request: GoodsSearchRequest | undefined,
    produce: (result: string) => NetworkResponse<T>, responseIds: (data: T | null) => number[]): Promise<NetworkResponse<T>> {
    const record: FixtureRequestRecord = new FixtureRequestRecord(++this.sequence, instanceId, scenario, kind, request);
    return new Promise<NetworkResponse<T>>((resolve, reject): void => {
      this.operations.set(record.id, new FixturePendingOperation((result: string): void => {
        const response: NetworkResponse<T> = produce(result);
        record.state = "resolved";
        record.completedAt = Date.now();
        record.responseJson = JSON.stringify(response);
        record.responseIds = responseIds(response.data);
        record.responseCode = response.code;
        this.operations.delete(record.id);
        this.records = this.records.slice();
        this.log("resolve", record);
        resolve(response);
      }, (): void => {
        record.state = "rejected";
        record.error = `fixture transport failure ${record.id}`;
        record.completedAt = Date.now();
        this.operations.delete(record.id);
        this.records = this.records.slice();
        this.log("reject", record);
        reject(new Error(`fixture transport failure ${record.id}`));
      }));
      this.records = [...this.records, record];
      this.log("request", record);
    });
  }

  resolve(id: number, result: string): void {
    const operation: FixturePendingOperation | undefined = this.operations.get(id);
    if (operation === undefined) { this.note(`unknown pending request ${id}`); return; }
    operation.resolve(result);
  }

  reject(id: number): void {
    const operation: FixturePendingOperation | undefined = this.operations.get(id);
    if (operation === undefined) { this.note(`unknown pending request ${id}`); return; }
    operation.reject();
  }

  note(message: string): void {
    this.eventSeq++;
    this.lastEvent = message;
    console.info(`[CML24FixtureControl] seq=${this.eventSeq} ${message}`);
  }

  private log(event: string, record: FixtureRequestRecord): void {
    this.eventSeq++;
    this.lastEvent = `${event} id=${record.id} instance=${record.instanceId} kind=${record.kind} page=${record.request?.page ?? 0}`;
    console.info("[CML24Fixture] " + JSON.stringify(new FixtureAuditEvent(this.eventSeq, event, record)));
    const text: string = JSON.stringify(record);
    const count: number = Math.ceil(text.length / 650);
    for (let index: number = 0; index < count; index++) {
      console.info(`[CML24FixtureRaw] seq=${this.eventSeq} event=${event} part=${index + 1}/${count} ` +
        text.substring(index * 650, (index + 1) * 650));
    }
  }
}
