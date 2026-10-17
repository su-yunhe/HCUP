# 二进制与大体量数据资源清单

`changes/final.diff` 用 `git diff --binary` 生成；经 `git diff --numstat` 核对，base_commit 到提交版本的全部改动中**没有二进制文件**（numstat 中无 `-` 行），因此无需另行存放二进制资源。

下列 21 个文件是新增的内置成语种子数据（文本 JSON，内容已完整包含在 `final.diff` 中）。因体量大（合计 23,241,388 字节），在此单列路径、大小与 SHA-256，便于核验与 diff 比对。
它们**不是**复制自基线自带资源：基线 `chinese_idiom` 表初始为空，数据由会话期间从应用公开数据接口下载后裁剪、分片生成，来源见 `sources.fragment.md`。

| 路径（相对工程根） | 大小（字节） | SHA-256 |
| --- | --- | --- |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/manifest.json` | 453 | `3163b35b54bc9fda43659531ac6a663e337888d5f1fdc252b7c5ee5bb6e29e93` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_01.json` | 1226739 | `35e28e623ee502a42a9d0c81ed9f7bc0be7ff8b32d2cf3b94a8f497e50d0ef1b` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_02.json` | 1189244 | `fee6643729e95e52bd041ce1b4257df55fa180395293b5e734788f9fe2e1f2fe` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_03.json` | 1192038 | `183b00a5bbc4710bdd8fa795b615f40f5382adc121e9e4247bac87d25c73fb9e` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_04.json` | 1170733 | `204adfe4d92efa0361d8eafc18d31861eb36dba420397e4519fa8977e6a109e1` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_05.json` | 1186912 | `e0e429cb3f9b8790c6e7985ce45caf223ba8ad8c579de61daa6a6cb880520bc4` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_06.json` | 1217272 | `2dcf2344e1fa9e9a21d96f6e267251a9a059d8cd86b9c118c132982f0f8c2ed2` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_07.json` | 1168513 | `91d4d882669c174d35de1662c7cb620dc961c0b9991078172f63c4482831ec29` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_08.json` | 1169757 | `15435242d606a931fefc53ab3db9e7bbf6beb0eb6a4a70455274aa82c8d27f7f` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_09.json` | 1157010 | `5443f9cfa893db319ed3ac5fb42f611a16b9a3b1159c4bef3316b21d4d7dad57` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_10.json` | 1150180 | `79df3953d8bc394121266f494e677d508f52e01691456b284428099a55af4fc4` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_11.json` | 1162330 | `9b971a88387780430bcc5eee63ca2458f862c65dfafb86e4280e3d7c7a6f6c7e` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_12.json` | 1152281 | `a0167f9eb4c2d072ca53966ba052bc093940fc3fbfa799e514d53e2e137d34bb` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_13.json` | 1176979 | `f1d171b88f0a77d4319e964cbbe15a22b6f089c3a3ce752054bbcd298b203e43` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_14.json` | 1143783 | `9022d9b9992dd9faea8329df6ba53e788ade647a08db395e0839fe45f9bf2b7a` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_15.json` | 1182462 | `f01122097987aedbc1a7f0005090030df33d202708744d5aab244a911cf89da3` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_16.json` | 1165487 | `2d248930af795c646e5e38c3dd5cc908c7055685baaf39441c693d3755e390f1` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_17.json` | 1142911 | `14003215eb899e51cbb06a313488e667bf6f8c6e9da8db24bda1e2241b339df4` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_18.json` | 1126099 | `61b1bd7171780066006fd26f3b5b33b1e5f24178ca2975f0564105b9f083f359` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_19.json` | 1160731 | `f3ea775ebd10a5b799d5d90b8826747cd547f614d532c414deef87b69354bb48` |
| `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/part_20.json` | 999474 | `81eb40a8acd49a7519d2d6750bdc9cae94f5f8062f564db8f4ca114916f7f170` |
