"""Unit tests: score_file"""

import pytest

CONDITION = {
    "default": {
        "labels": ["default"],
        "modifier": 0,
    },
    "arch": {
        "labels": ["a", "arch"],
        "modifier": 1,
    },
    "system": {
        "labels": ["o", "os"],
        "modifier": 2,
    },
    "distro": {
        "labels": ["d", "distro"],
        "modifier": 4,
    },
    "distro_family": {
        "labels": ["f", "distro_family"],
        "modifier": 8,
    },
    "class": {
        "labels": ["c", "class"],
        "modifier": 16,
    },
    "hostname": {
        "labels": ["h", "hostname"],
        "modifier": 32,
    },
    "user": {
        "labels": ["u", "user"],
        "modifier": 64,
    },
}
TEMPLATE_LABELS = ["t", "template", "yadm"]


def calculate_score(filename):
    """Calculate the expected score"""
    # pylint: disable=too-many-branches
    score = 0

    _, conditions = filename.split("##", 1)

    for condition in conditions.split(","):
        label = condition
        value = None
        if "." in condition:
            label, value = condition.split(".", 1)
        if label in CONDITION["default"]["labels"]:
            score += 1000
        elif label in CONDITION["arch"]["labels"]:
            if value.lower() == "testarch":
                score += 1000 + CONDITION["arch"]["modifier"]
            else:
                score = 0
                break
        elif label in CONDITION["system"]["labels"]:
            if value.lower() == "testsystem":
                score += 1000 + CONDITION["system"]["modifier"]
            else:
                score = 0
                break
        elif label in CONDITION["distro"]["labels"]:
            if value.lower() == "testdistro":
                score += 1000 + CONDITION["distro"]["modifier"]
            else:
                score = 0
                break
        elif label in CONDITION["class"]["labels"]:
            if value.lower() == "testclass":
                score += 1000 + CONDITION["class"]["modifier"]
            else:
                score = 0
                break
        elif label in CONDITION["hostname"]["labels"]:
            if value.lower() == "testhost":
                score += 1000 + CONDITION["hostname"]["modifier"]
            else:
                score = 0
                break
        elif label in CONDITION["user"]["labels"]:
            if value.lower() == "testuser":
                score += 1000 + CONDITION["user"]["modifier"]
            else:
                score = 0
                break
        elif label not in TEMPLATE_LABELS:
            score = 0
            break
    return score


@pytest.mark.parametrize("default", ["default", None], ids=["default", "no-default"])
@pytest.mark.parametrize("arch", ["arch", None], ids=["arch", "no-arch"])
@pytest.mark.parametrize("system", ["system", None], ids=["system", "no-system"])
@pytest.mark.parametrize("distro", ["distro", None], ids=["distro", "no-distro"])
@pytest.mark.parametrize("cla", ["class", None], ids=["class", "no-class"])
@pytest.mark.parametrize("host", ["hostname", None], ids=["hostname", "no-host"])
@pytest.mark.parametrize("user", ["user", None], ids=["user", "no-user"])
def test_score_values(runner, yadm, default, arch, system, distro, cla, host, user):
    """Test score results"""
    # pylint: disable=too-many-branches
    local_class = "testClass"
    local_arch = "testARch"
    local_system = "TESTsystem"
    local_distro = "testDISTro"
    local_host = "testHost"
    local_user = "testUser"
    filenames = {"filename##": 0}

    if default:
        for filename in list(filenames):
            for label in CONDITION[default]["labels"]:
                newfile = filename
                if not newfile.endswith("##"):
                    newfile += ","
                newfile += label
                filenames[newfile] = calculate_score(newfile)
    if arch:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[arch]["labels"]:
                    newfile = filename
                    if not newfile.endswith("##"):
                        newfile += ","
                    newfile += ".".join([label, local_arch if match else "badarch"])
                    filenames[newfile] = calculate_score(newfile)
    if system:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[system]["labels"]:
                    newfile = filename
                    if not newfile.endswith("##"):
                        newfile += ","
                    newfile += ".".join([label, local_system if match else "badsys"])
                    filenames[newfile] = calculate_score(newfile)
    if distro:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[distro]["labels"]:
                    newfile = filename
                    if not newfile.endswith("##"):
                        newfile += ","
                    newfile += ".".join([label, local_distro if match else "baddistro"])
                    filenames[newfile] = calculate_score(newfile)
    if cla:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[cla]["labels"]:
                    newfile = filename
                    if not newfile.endswith("##"):
                        newfile += ","
                    newfile += ".".join([label, local_class if match else "badclass"])
                    filenames[newfile] = calculate_score(newfile)
    if host:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[host]["labels"]:
                    newfile = filename
                    if not newfile.endswith("##"):
                        newfile += ","
                    newfile += ".".join([label, local_host if match else "badhost"])
                    filenames[newfile] = calculate_score(newfile)
    if user:
        for filename in list(filenames):
            for match in [True, False]:
                for label in CONDITION[user]["labels"]:
                    newfile = filename
                    if not newfile.endswith("##"):
                        newfile += ","
                    newfile += ".".join([label, local_user if match else "baduser"])
                    filenames[newfile] = calculate_score(newfile)

    script = f"""
        YADM_TEST=1 source {yadm}
        score=0
        local_class={local_class}
        local_classes=({local_class})
        local_arch={local_arch}
        local_system={local_system}
        local_distro={local_distro}
        local_host={local_host}
        local_user={local_user}
    """
    expected = ""
    for filename, score in filenames.items():
        script += f"""
            score_file "{filename}" "dest"
            echo "{filename}"
            echo "$score"
        """
        expected += filename + "\n"
        expected += str(score) + "\n"
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert run.out == expected


@pytest.mark.parametrize("ext", [None, "e", "extension"])
def test_extensions(runner, yadm, ext):
    """Verify extensions do not effect scores"""
    local_user = "testuser"
    filename = f"filename##u.{local_user}"
    if ext:
        filename += f",{ext}.xyz"
    expected = ""
    script = f"""
        YADM_TEST=1 source {yadm}
        score=0
        local_user={local_user}
        score_file "{filename}"
        echo "$score"
    """
    expected = f'{1000 + CONDITION["user"]["modifier"]}\n'
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert run.out == expected


def test_score_values_templates(runner, yadm):
    """Test score results"""
    local_class = "testclass"
    local_arch = "arch"
    local_system = "testsystem"
    local_distro = "testdistro"
    local_host = "testhost"
    local_user = "testuser"
    filenames = {"filename##": 0}

    for filename in list(filenames):
        for label in TEMPLATE_LABELS:
            newfile = filename
            if not newfile.endswith("##"):
                newfile += ","
            newfile += ".".join([label, "testtemplate"])
            filenames[newfile] = calculate_score(newfile)

    script = f"""
        YADM_TEST=1 source {yadm}
        score=0
        local_class={local_class}
        local_arch={local_arch}
        local_system={local_system}
        local_distro={local_distro}
        local_host={local_host}
        local_user={local_user}
    """
    expected = ""
    for filename, score in filenames.items():
        script += f"""
            score_file "{filename}" "dest"
            echo "{filename}"
            echo "$score"
        """
        expected += filename + "\n"
        expected += str(score) + "\n"
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert run.out == expected


@pytest.mark.parametrize("processor_generated", [True, False], ids=["supported-template", "unsupported-template"])
def test_template_recording(runner, yadm, processor_generated):
    """Template should be recorded if choose_template_processor outputs a command"""

    mock = "function choose_template_processor() { return; }"
    expected = ""
    if processor_generated:
        mock = 'function choose_template_processor() { echo "test_processor"; }'
        expected = "template recorded"

    script = f"""
        YADM_TEST=1 source {yadm}
        function record_score() {{ [ -n "$4" ] && echo "template recorded"; }}
        {mock}
        score_file "testfile##template.kind"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert run.out.rstrip() == expected


def test_underscores_and_upper_case_in_distro_and_family(runner, yadm):
    """Test replacing spaces with underscores and lowering case in distro / distro_family"""
    local_distro = "test distro"
    local_distro_family = "test family"
    filenames = {
        "filename##distro.Test Distro": 1004,
        "filename##distro.test-distro": 0,
        "filename##distro.test_distro": 1004,
        "filename##distro_family.test FAMILY": 1008,
        "filename##distro_family.test-family": 0,
        "filename##distro_family.test_family": 1008,
    }

    script = f"""
        YADM_TEST=1 source {yadm}
        score=0
        local_distro="{local_distro}"
        local_distro_family="{local_distro_family}"
    """
    expected = ""
    for filename, score in filenames.items():
        script += f"""
            score_file "{filename}"
            echo "{filename}"
            echo "$score"
        """
        expected += filename + "\n"
        expected += str(score) + "\n"
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert run.out == expected


def test_negative_class_condition(runner, yadm):
    """Test negative class condition: returns 0 when matching and proper score when not matching."""
    script = f"""
        YADM_TEST=1 source {yadm}
        local_class="testclass"
        local_classes=("testclass")

        # 0
        score=0
        score_file "filename##~class.testclass" "dest"
        echo "score: $score"

        # 16
        score=0
        score_file "filename##~class.badclass" "dest"
        echo "score2: $score"

        # 16
        score=0
        score_file "filename##~c.badclass" "dest"
        echo "score3: $score"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    output = run.out.strip().splitlines()
    assert output[0] == "score: 0"
    assert output[1] == "score2: 16"
    assert output[2] == "score3: 16"


def test_negative_combined_conditions(runner, yadm):
    """Test negative conditions for multiple alt types: returns 0 when matching and proper score when not matching."""
    script = f"""
        YADM_TEST=1 source {yadm}
        local_class="testclass"
        local_classes=("testclass")
        local_distro="testdistro"

        # (0) + (0) = 0
        score=0
        score_file "filename##~class.testclass,~distro.testdistro" "dest"
        echo "score: $score"

        # (1000 + 16) + (1000 + 4) = 2020
        score=0
        score_file "filename##class.testclass,distro.testdistro" "dest"
        echo "score2: $score"

        # 0 (negated class condition)
        score=0
        score_file "filename##~class.badclass,~distro.testdistro" "dest"
        echo "score3: $score"

        # (1000 + 16) + (4) = 1020
        score=0
        score_file "filename##class.testclass,~distro.baddistro" "dest"
        echo "score4: $score"

        # (1000 + 16) + (16) = 1032
        score=0
        score_file "filename##class.testclass,~class.badclass" "dest"
        echo "score5: $score"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    output = run.out.strip().splitlines()
    assert output[0] == "score: 0"
    assert output[1] == "score2: 2020"
    assert output[2] == "score3: 0"
    assert output[3] == "score4: 1020"
    assert output[4] == "score5: 1032"
