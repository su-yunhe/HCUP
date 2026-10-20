# Material collection attempts

- First `python .comate/submission-draft/tools/prepare_materials.py collect` exited 1 with `AttributeError: NoneType object has no attribute get` while parsing a native token_count event whose info was null. The actual command, traceback and subsequent patch are retained in this materials main native session (01a14823-79c4-78f3-b80d-737ef7fb7799).
- Updated only the material parser to treat null token info as absent; reran the same collection command and it exited 0. No production, resource or build configuration changed.
- Historical product/test failures are retained in source logs and native development records; this note does not replace them.

- First diff validation: clone/checkout/apply --check/actual apply all exited 0, but 111 exact-byte mismatches were found because text=auto still selected CRLF even with core.autocrlf=false. Original failure report retained as diff-validation-attempt1.json. A clone-local .git/info/attributes override disables text/filter/working-tree-encoding conversion; global config and task sources remain untouched. The revised validation is recorded separately.

- Second validator invocation occurred before the asynchronous replacement snapshot finished, so it still read the first manifest. Clone reconstruction had zero missing/extra/clone hash mismatches after the attributes fix, but three live material files (README and two tools) no longer matched that superseded manifest. Preserved as diff-validation-attempt2.json. The next invocation must wait for snapshot completion; no test/product assertions were weakened.
