# 非空SQLite WAL成套保留策略独立复审

实际线程 `01a14f55-5f14-7860-976f-10407965f444`。仅写本validation目录，未改workflow冻结文件、原数据库、canonical副本、生产或设备，未启服务。本次只读原文件stat/字节SHA，没有sqlite3连接。

**策略接受，但采集/完整性结果尚未签核。** 独立当前枚举确认5个非空WAL及各自主DB均存在，WAL合计16,595,520字节；连续两次读取的大小/mtime_ns/SHA完全相同。对应三份host-protocol、boundary/verification/runtime和fixture-ui/evidence。原件列表/每文件hash见`submit-materials-wal-inventory-01.json`。这只是当时只读稳定性，不冒充worker复制区间或逻辑完整性。

直接排除全部WAL有丢掉尚未归入主DB的提交页风险。Root改为保留原同目录、同名主DB＋非空WAL固定证据，并仅排空WAL、SHM/journal，是正确的保全方向。官方清单禁止的是“仍在写入”的数据库临时文件；必须附已有服务清理、无后续写者、冻结和稳定采集证据，不能只以文件非空或一次hash就称已停写。

初审workflow中的通用临时sidecar排除建议保持原件；本次scope显式修订五个非空WAL例外，不用回改已冻结project中的旧报告。五个明确include必须优先于泛化的sidecar/runtime排除规则；不可为了减少diff把静态主DB/WAL当缓存漏掉。

## 终审必须看到的证据

1. 成套读取主DB/WAL的复制前path、size、mtime_ns、SHA；两文件都复制完后再取原两文件同字段。各canonical文件须与原SHA/大小一致，原前后完全不变。保留原始配对文件名/相对目录。
2. 原DB与canonical副本均不许用SQLite打开、checkpoint、修复。复制canonical成套文件到独立validation审计目录，在此逻辑DB+WAL视图执行PRAGMA integrity_check，保存实际连接参数、SQLite版本、原始结果/错误与退出码；不能只校验裸主DB就宣称覆盖了WAL。
3. 尽可能记表名/行数或对应逻辑状态，证明证据可读。integrity=ok只属静态存储检查，不是地址功能/正式AUTH通过。审计产生的SHM、WAL变化或checkpoint只能影响一次性审计副本。
4. 审计后再次hash/stat canonical主DB＋WAL，必须完全未变。审计副本/校验报告位于明确排除的validation树，避免进入project自包含。
5. 任一伙伴缺失、前后变化、复制不符、打开失败或integrity非ok均fail/停止，不静默丢WAL、补造空库或修canonical来通过。

当前W01策略、W02只读枚举通过；W03复制/成套稳定、W04审计副本完整性、W05最终manifest五对覆盖均not_run，待Root/worker产物。final.diff/clone完整性仍未签核；scope须透明说明WAL例外，不概括为“全部规则无例外”。
