"""Use the unchanged common runner, selecting local debugging cases by name."""
import os
import sys
import unittest
import harness.runner as runner

original = runner.discover
selection = os.environ.get("VG14_CASE_FILTER", "").split(",")

def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case

def discover(project):
    cases = [case for case in flatten(original(project)) if any(part in str(case) for part in selection)]
    if not cases:
        raise RuntimeError("No tests matched the explicit batch selection")
    return unittest.TestSuite(cases)

runner.discover = discover
sys.exit(runner.main())
