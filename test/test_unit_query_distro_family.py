"""Unit tests: query_distro_family"""

import pytest


@pytest.mark.parametrize("condition", ["os-release", "os-release-quotes", "missing", "fallback"])
def test_query_distro_family(runner, yadm, tmp_path, condition):
    """Match ID_LIKE when present"""
    test_family = "testfamily"
    os_release = tmp_path.joinpath("os-release")
    if "os-release" in condition:
        quotes = '"' if "quotes" in condition else ""
        os_release.write_text(f"testing\nID=test\nID_LIKE={quotes}{test_family}{quotes}\nfamily")
    elif condition == "fallback":
        os_release.write_text(f'testing\nID="{test_family}"\nfamily')
    script = f"""
        YADM_TEST=1 source {yadm}
        OS_RELEASE="{os_release}"
        query_distro_family
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    if condition == "missing":
        assert run.out.rstrip() == ""
    else:
        assert run.out.rstrip() == test_family
