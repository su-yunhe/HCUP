# 材料终审发现与修复闭环

独立验证报告保留其当时的结论，不改写历史失败。该报告审核的是先前e68d截点；随后仅workflow/state.json和events.jsonl登记了本材料阶段与下一步，生产代码、资源和产品配置没有变动。

M1（已修复）：先前清单宣称按相对路径字符串排序生成ID，脚本却使用WindowsPath大小写排序，独立重算不一致。freeze_project.py已明确使用字符串path排序，verify_materials.py独立按声明算法重算。当前 snapshot_id=`1b5799251641879b65b9daed9c3a8073439773ab7f0692901ecd6103c81921e3`，独立重算=`1b5799251641879b65b9daed9c3a8073439773ab7f0692901ecd6103c81921e3`，两者相同。最终完整性报告 checks/material-integrity.json 还会再次核对。逐文件和补丁内容的旧审查结论未被当作新ID通过证明。

R1（已修复）：首轮临时clone的Windows native换行导致apply-check失败。临时clone显式core.autocrlf=false、core.eol=lf后，重新checkout基线并生成补丁；当前apply-check与实际apply均退出0，776份文件全字节还原，见diff-validation.json。277项基线checkout换行保留条目不是功能改动；原始文本空白警告仍在patch-whitespace.log，不用改日志来消除警告。

隐私处理：材料会话工具输出中的无关侧边栏索引行局部替换，实际替换行及前后摘要见trace-redactions.json。8份解题线程、源码依据和失败/重试没有被裁掉。

尚未关闭的是用户输入和可核实记录缺口，见pending-fields.md；它们不被技术校验pass覆盖。没有补跑设备或构建；正式打包未执行。
