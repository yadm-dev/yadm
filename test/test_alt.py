"""Test alt"""

import os
import string

import py
import pytest
import utils

TEST_PATHS = [utils.ALT_FILE1, utils.ALT_FILE2, utils.ALT_DIR]


@pytest.mark.usefixtures("ds1_copy")
@pytest.mark.parametrize("yadm_alt", [True, False], ids=["alt", "worktree"])
@pytest.mark.parametrize(
    "tracked,encrypt,exclude",
    [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, True, True),
    ],
    ids=["untracked", "tracked", "encrypted", "excluded"],
)
def test_alt_source(runner, paths, tracked, encrypt, exclude, yadm_alt):
    """Test yadm alt operates on all expected sources of alternates"""
    yadm_dir, yadm_data = setup_standard_yadm_dir(paths)

    utils.create_alt_files(
        paths, "##default", tracked=tracked, encrypt=encrypt, exclude=exclude, yadm_alt=yadm_alt, yadm_dir=yadm_dir
    )
    run = runner([paths.pgm, "-Y", yadm_dir, "--yadm-data", yadm_data, "alt"])
    assert run.success
    assert run.err == ""
    linked = utils.parse_alt_output(run.out)

    basepath = yadm_dir.join("alt") if yadm_alt else paths.work

    for link_path in TEST_PATHS:
        source_file_content = link_path + "##default"
        source_file = basepath.join(source_file_content)
        link_file = paths.work.join(link_path)
        if link_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            link_file = link_file.join(utils.CONTAINED)
        if tracked or (encrypt and not exclude):
            assert link_file.islink()
            target = py.path.local(os.path.realpath(link_file))
            assert target.isfile()
            assert link_file.read() == source_file_content
            assert str(source_file) in linked
        else:
            assert not link_file.exists()
            assert str(source_file) not in linked


@pytest.mark.usefixtures("ds1_copy")
@pytest.mark.parametrize("yadm_alt", [True, False], ids=["alt", "worktree"])
def test_relative_link(runner, paths, yadm_alt):
    """Confirm links created are relative"""
    yadm_dir, yadm_data = setup_standard_yadm_dir(paths)

    utils.create_alt_files(
        paths, "##default", tracked=True, encrypt=False, exclude=False, yadm_alt=yadm_alt, yadm_dir=yadm_dir
    )
    run = runner([paths.pgm, "-Y", yadm_dir, "--yadm-data", yadm_data, "alt"])
    assert run.success
    assert run.err == ""

    basepath = yadm_dir.join("alt") if yadm_alt else paths.work

    for link_path in TEST_PATHS:
        source_file_content = link_path + "##default"
        source_file = basepath.join(source_file_content)
        link_file = paths.work.join(link_path)
        if link_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            link_file = link_file.join(utils.CONTAINED)
        link = link_file.readlink()
        relpath = os.path.relpath(source_file, start=os.path.dirname(link_file))
        assert link == relpath


@pytest.mark.usefixtures("ds1_copy")
@pytest.mark.parametrize(
    "suffix",
    [
        "##default",
        "##default,e.txt",
        "##default,extension.txt",
        "##a.$tst_arch",
        "##arch.$tst_arch",
        "##o.$tst_sys",
        "##os.$tst_sys",
        "##d.$tst_distro",
        "##distro.$tst_distro",
        "##f.$tst_distro_family",
        "##distro_family.$tst_distro_family",
        "##c.$tst_class",
        "##class.$tst_class",
        "##h.$tst_host",
        "##hostname.$tst_host",
        "##u.$tst_user",
        "##user.$tst_user",
    ],
)
def test_alt_conditions(runner, paths, tst_arch, tst_sys, tst_distro, tst_distro_family, tst_host, tst_user, suffix):
    """Test conditions supported by yadm alt"""
    yadm_dir, yadm_data = setup_standard_yadm_dir(paths)

    # set the class
    tst_class = "testclass"
    utils.set_local(paths, "class", tst_class + ".before")
    utils.set_local(paths, "class", tst_class, add=True)
    utils.set_local(paths, "class", tst_class + ".after", add=True)

    suffix = string.Template(suffix).substitute(
        tst_arch=tst_arch,
        tst_sys=tst_sys,
        tst_distro=tst_distro,
        tst_distro_family=tst_distro_family,
        tst_class=tst_class,
        tst_host=tst_host,
        tst_user=tst_user,
    )

    utils.create_alt_files(paths, suffix)
    run = runner([paths.pgm, "-Y", yadm_dir, "--yadm-data", yadm_data, "alt"])
    assert run.success
    assert run.err == ""
    linked = utils.parse_alt_output(run.out)

    for link_path in TEST_PATHS:
        source_file_content = link_path + suffix
        source_file = paths.work.join(source_file_content)
        link_file = paths.work.join(link_path)
        if link_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            link_file = link_file.join(utils.CONTAINED)
        assert link_file.islink()
        target = py.path.local(os.path.realpath(link_file))
        assert target.isfile()
        assert link_file.read() == source_file_content
        assert str(source_file) in linked


@pytest.mark.usefixtures("ds1_copy")
@pytest.mark.parametrize("kind", ["default", "", None, "envtpl", "j2cli", "j2", "esh"])
@pytest.mark.parametrize(
    "label",
    [
        "t",
        "template",
        "yadm",
    ],
)
def test_alt_templates(runner, paths, kind, label):
    """Test templates supported by yadm alt"""
    yadm_dir, yadm_data = setup_standard_yadm_dir(paths)

    suffix = f"##{label}.{kind}"
    if kind is None:
        suffix = f"##{label}"

    utils.create_alt_files(paths, suffix)
    run = runner([paths.pgm, "-Y", yadm_dir, "--yadm-data", yadm_data, "alt"])
    assert run.success
    assert run.err == ""
    created = utils.parse_alt_output(run.out, linked=False)

    for created_path in TEST_PATHS:
        source_file_content = created_path + suffix
        source_file = paths.work.join(source_file_content)
        created_file = paths.work.join(created_path)
        if created_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            created_file = created_file.join(utils.CONTAINED)
        assert created_file.isfile()
        assert created_file.read().strip() == source_file_content
        assert str(source_file) in created


@pytest.mark.usefixtures("ds1_copy")
def test_alt_template_with_condition(runner, paths, tst_arch):
    """Test template with extra condition"""
    yadm_dir, yadm_data = setup_standard_yadm_dir(paths)

    suffix = f"##template,arch.not{tst_arch}"
    utils.create_alt_files(paths, suffix)
    run = runner([paths.pgm, "-Y", yadm_dir, "--yadm-data", yadm_data, "alt"])
    assert run.success
    assert run.err == ""

    created = utils.parse_alt_output(run.out, linked=False)
    assert len(created) == 0


@pytest.mark.usefixtures("ds1_copy")
@pytest.mark.parametrize("autoalt", [None, "true", "false"])
def test_auto_alt(runner, yadm_cmd, paths, autoalt):
    """Test auto alt"""

    # set the value of auto-alt
    if autoalt:
        os.system(" ".join(yadm_cmd("config", "yadm.auto-alt", autoalt)))

    utils.create_alt_files(paths, "##default")
    run = runner(yadm_cmd("status"))
    assert run.success
    assert run.err == ""
    linked = utils.parse_alt_output(run.out)

    for link_path in TEST_PATHS:
        source_file_content = link_path + "##default"
        source_file = paths.work.join(source_file_content)
        link_file = paths.work.join(link_path)
        if link_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            link_file = link_file.join(utils.CONTAINED)

        if autoalt == "false":
            assert not link_file.exists()
        else:
            assert link_file.islink()
            target = py.path.local(os.path.realpath(link_file))
            assert target.isfile()
            assert link_file.read() == source_file_content
            # no linking output when run via auto-alt
            assert str(source_file) not in linked


@pytest.mark.usefixtures("ds1_copy")
@pytest.mark.parametrize("autoexclude", [None, "true", "false"])
def test_alt_exclude(runner, yadm_cmd, paths, autoexclude):
    """Test alt exclude"""

    # set the value of auto-exclude
    if autoexclude:
        os.system(" ".join(yadm_cmd("config", "yadm.auto-exclude", autoexclude)))

    utils.create_alt_files(paths, "##default")
    run = runner(yadm_cmd("alt", "-d"))
    assert run.success

    run = runner(yadm_cmd("status", "-z", "-uall", "--ignored"))
    assert run.success
    assert run.err == ""
    status = run.out.split("\0")

    for link_path in TEST_PATHS:
        if link_path == utils.ALT_DIR:
            link_path = f"{link_path}/{utils.CONTAINED}"
        flags = "??" if autoexclude == "false" else "!!"
        assert f"{flags} {link_path}" in status


@pytest.mark.usefixtures("ds1_copy")
def test_stale_link_removal(runner, yadm_cmd, paths):
    """Stale links to alternative files are removed

    This test ensures that when an already linked alternative becomes invalid
    due to a change in class, the alternate link is removed.
    """

    # set the class
    tst_class = "testclass"
    utils.set_local(paths, "class", tst_class)

    # create files which match the test class
    utils.create_alt_files(paths, f"##class.{tst_class}")

    # run alt to trigger linking
    run = runner(yadm_cmd("alt"))
    assert run.success
    assert run.err == ""
    linked = utils.parse_alt_output(run.out)

    # assert the proper linking has occurred
    for link_path in TEST_PATHS:
        source_file_content = link_path + f"##class.{tst_class}"
        source_file = paths.work.join(source_file_content)
        link_file = paths.work.join(link_path)
        if link_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            link_file = link_file.join(utils.CONTAINED)
        assert link_file.islink()
        target = py.path.local(os.path.realpath(link_file))
        assert target.isfile()
        assert link_file.read() == source_file_content
        assert str(source_file) in linked

    # change the class so there are no valid alternates
    utils.set_local(paths, "class", "changedclass")

    # run alt to trigger linking
    run = runner(yadm_cmd("alt"))
    assert run.success
    assert run.err == ""
    linked = utils.parse_alt_output(run.out)

    # assert the linking is removed
    for stale_path in TEST_PATHS:
        source_file_content = stale_path + f"##class.{tst_class}"
        source_file = paths.work.join(source_file_content)
        stale_file = paths.work.join(stale_path)
        if stale_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            stale_file = stale_file.join(utils.CONTAINED)
        assert not stale_file.exists()
        assert str(source_file) not in linked


@pytest.mark.usefixtures("ds1_copy")
def test_legacy_dir_link_removal(runner, yadm_cmd, paths):
    """Legacy link to alternative dir is removed

    This test ensures that a legacy dir alternative (i.e. symlink to the dir
    itself) is converted to indiividual links.
    """

    utils.create_alt_files(paths, "##default")

    # Create legacy link
    link_dir = paths.work.join(utils.ALT_DIR)
    link_dir.mksymlinkto(link_dir.basename + "##default")
    assert link_dir.islink()

    # run alt to trigger linking
    run = runner(yadm_cmd("alt"))
    assert run.success
    assert run.err == ""
    linked = utils.parse_alt_output(run.out)

    # assert legacy link is removed
    assert not link_dir.islink()

    # assert the proper linking has occurred
    for link_path in TEST_PATHS:
        source_file_content = link_path + "##default"
        source_file = paths.work.join(source_file_content)
        link_file = paths.work.join(link_path)
        if link_path == utils.ALT_DIR:
            source_file = source_file.join(utils.CONTAINED)
            link_file = link_file.join(utils.CONTAINED)
        assert link_file.islink()
        target = py.path.local(os.path.realpath(link_file))
        assert target.isfile()
        assert link_file.read() == source_file_content
        assert str(source_file) in linked


@pytest.mark.usefixtures("ds1_repo_copy")
def test_template_overwrite_symlink(runner, yadm_cmd, paths, tst_sys):
    """Remove symlinks before processing a template

    If a symlink is in the way of the output of a template, the target of the
    symlink will get the template content. To prevent this, the symlink should
    be removed just before processing a template.
    """

    target = paths.work.join(f"test_link##os.{tst_sys}")
    target.write("target")

    link = paths.work.join("test_link")
    link.mksymlinkto(target, absolute=1)

    template = paths.work.join("test_link##template.default")
    template.write("test-data")

    run = runner(yadm_cmd("add", target, template))
    assert run.success
    assert run.err == ""
    assert run.out == ""
    assert not link.islink()
    assert target.read().strip() == "target"
    assert link.read().strip() == "test-data"


@pytest.mark.usefixtures("ds1_copy")
@pytest.mark.parametrize("style", ["symlink", "template"])
def test_ensure_alt_path(runner, paths, style):
    """Test that directories are created before making alternates"""
    yadm_dir, yadm_data = setup_standard_yadm_dir(paths)
    suffix = "default" if style == "symlink" else "template"
    filename = "a/b/c/file"
    source = yadm_dir.join(f"alt/{filename}##{suffix}")
    source.write("test-data", ensure=True)
    run = runner([paths.pgm, "-Y", yadm_dir, "--yadm-data", yadm_data, "add", source])
    assert run.success
    assert run.err == ""
    assert run.out == ""
    assert paths.work.join(filename).read().strip() == "test-data"


def setup_standard_yadm_dir(paths):
    """Configure a yadm home within the work tree"""
    std_yadm_dir = paths.work.mkdir(".config").mkdir("yadm")
    std_yadm_data = paths.work.mkdir(".local").mkdir("share").mkdir("yadm")
    std_yadm_data.join("repo.git").mksymlinkto(paths.repo, absolute=1)
    std_yadm_dir.join("encrypt").mksymlinkto(paths.encrypt, absolute=1)
    return std_yadm_dir, std_yadm_data
