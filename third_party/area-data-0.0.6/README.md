# area-data 0.0.6 attribution

Author: ibestservices. License: Apache-2.0 (full original LICENSE retained).

Official registry: https://ohpm.openharmony.cn/ohpm/@ibestservices/area-data

Original HAR: https://ohpm.openharmony.cn/ohpm/@ibestservices/area-data/-/area-data-0.0.6.har

HAR SHA256: `ca85c6c34537371024e4a3199922b8cd22ca359d5931ff2d4c6b48cc66cb248d`.

Original `src/main/ets/model/AreaData.ets` SHA256: `220a240d5412206e66d271c3bfb3693fc528fa3d23d972c902e4bb78e0c5dc82`.

Modified representation: complete regionData text/value/children tree is stored as typed static ETS data; names, codes, order, parent relationships and all 34 provinces / 369 cities / 3477 districts are retained. Package resources, formatter functions, other exports and GeoJSON are not included. The original package has no NOTICE file.

Reproduce from this project root: `python workflow/implementation/development-export-region-data.py`. The script verifies the original HAR/source SHA256, numeric-key ordering, all 3880 nodes, full paths, and exact UTF-8 canonical JSON equality against the independently captured original regionData. Canonical SHA256: `565f7e754dfca6640fabcdc71423a7b307ece4aa96f6a9def486ac01e327552b`. Evidence: `workflow/implementation/development-region-export-06.json`.
