# 材料核查时的客户端与工具版本

`app-version-probe.json`保存本次客户端只读工具的实际返回：installedVersion 26.1013.40934，build20770，prod。未下载、安装或重启；不以up_to_date状态为材料验收结论。当前已安装产品值不能反向证明所有旧会话发生时的桌面产品版本。

`ohpm-version-probe.json`保存仅执行`ohpm --version`的原stdout/exit，当前为6.1.1.830。只加载当前进程的已配置开发环境，没有执行依赖安装、构建或设备命令。旧构建期间没有对应独立版本日志，仍保留该历史限制。

初次16会话导出manifest在较早截点将桌面产品版本列为未核，这是当时状态；原manifest未改，本补证在trace-index/facts/build中单独并列，不伪造原始字段。原生cli_version 0.163.0-alpha.10.2仍按运行器字段保留。
