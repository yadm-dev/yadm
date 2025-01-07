"""Unit tests: set_operating_system"""

import pytest


@pytest.mark.parametrize(
    "proc_value, expected_os",
    [
        ("missing", "uname"),
        ("has microsoft inside", "WSL"),  # case insensitive
        ("has Microsoft inside", "WSL"),  # case insensitive
        ("another value", "uname"),
    ],
    ids=[
        "/proc/version missing",
        "/proc/version includes ms",
        "/proc/version excludes Ms",
        "another value",
    ],
)
def test_set_operating_system(runner, paths, tst_sys, proc_value, expected_os):
    """Run set_operating_system and test result"""

    # Normally /proc/version (set in PROC_VERSION) is inspected to identify
    # WSL. During testing, we will override that value.
    proc_version = paths.root.join("proc_version")
    proc_version.write(proc_value)
    script = f"""
        YADM_TEST=1 source {paths.pgm}
        PROC_VERSION={proc_version}
        set_operating_system
        echo $OPERATING_SYSTEM
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    if expected_os == "uname":
        if tst_sys != "WSL":
            expected_os = tst_sys
        else:
            expected_os = "Linux"
    assert run.out.rstrip() == expected_os
