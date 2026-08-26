"""Run the physics sanity harness as part of the test suite.

`scripts/sanity_check.py` holds the invariants the results rest on (limits that
must be reproduced exactly, monotonicity that cannot invert, published numbers
the deck quotes). Running it here means a change that breaks the physics fails
the suite rather than waiting to be noticed in a figure.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_sanity_harness_passes():
    result = subprocess.run(
        [sys.executable, os.path.join("scripts", "sanity_check.py")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "physics sanity harness failed:\n" + result.stdout[-3000:] + result.stderr[-2000:]
    )
    assert "ALL SANITY CHECKS PASS" in result.stdout
