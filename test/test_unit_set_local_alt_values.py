"""Unit tests: set_local_alt_values"""

import pytest
import utils


@pytest.mark.parametrize(
    "override",
    [
        False,
        "class",
        "arch",
        "os",
        "hostname",
        "user",
        "distro",
        "distro-family",
    ],
    ids=[
        "no-override",
        "override-class",
        "override-arch",
        "override-os",
        "override-hostname",
        "override-user",
        "override-distro",
        "override-distro-family",
    ],
)
@pytest.mark.usefixtures("ds1_copy")
def test_set_local_alt_values(
    runner, yadm, paths, tst_arch, tst_sys, tst_host, tst_user, tst_distro, tst_distro_family, override
):
    """Test handling of local alt values"""
    script = f"""
        YADM_TEST=1 source {yadm} &&
        set_operating_system &&
        YADM_DIR={paths.yadm} YADM_DATA={paths.data} configure_paths &&
        set_local_alt_values
        echo "class='$local_class'"
        echo "arch='$local_arch'"
        echo "os='$local_system'"
        echo "hostname='$local_host'"
        echo "user='$local_user'"
        echo "distro='$local_distro'"
        echo "distro-family='$local_distro_family'"
    """

    if override == "class":
        utils.set_local(paths, override, "first")
        utils.set_local(paths, override, "override", add=True)
    elif override:
        utils.set_local(paths, override, "override")

    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""

    default_values = {
        "class": "",
        "arch": tst_arch,
        "os": tst_sys,
        "hostname": tst_host,
        "user": tst_user,
        "distro": tst_distro,
        "distro-family": tst_distro_family,
    }

    for key, value in default_values.items():
        if key == override:
            assert f"{key}='override'" in run.out
        else:
            assert f"{key}='{value}'" in run.out
