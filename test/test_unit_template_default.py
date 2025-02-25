"""Unit tests: template_default"""

import os

FILE_MODE = 0o754

# these values are also testing the handling of bizarre characters
LOCAL_CLASS = "default_Test+@-!^Class"
LOCAL_CLASS2 = "default_Test+@-|^2nd_Class withSpace"
LOCAL_ARCH = "default_Test+@-!^Arch"
LOCAL_SYSTEM = "default_Test+@-!^System"
LOCAL_HOST = "default_Test+@-!^Host"
LOCAL_USER = "default_Test+@-!^User"
LOCAL_DISTRO = "default_Test+@-!^Distro"
LOCAL_DISTRO_FAMILY = "default_Test+@-!^Family"
ENV_VAR = "default_Test+@-!^Env"
TEMPLATE = f"""
start of template
default class         = >{{{{yadm.class}}}}<
default arch          = >{{{{yadm.arch}}}}<
default os            = >{{{{yadm.os}}}}<
default host          = >{{{{yadm.hostname}}}}<
default user          = >{{{{yadm.user}}}}<
default distro        = >{{{{yadm.distro}}}}<
default distro_family = >{{{{yadm.distro_family}}}}<
classes = >{{{{yadm.classes}}}}<
{{% if yadm.class == "else1" %}}
wrong else 1
{{% else %}}
Included section from else
{{% endif %}}
{{% if yadm.class == "wrongclass1" %}}
wrong class 1
{{% endif %}}
{{% if yadm.class != "wronglcass" %}}
Included section from !=
{{%     endif\t\t  %}}
{{% if yadm.class == "{LOCAL_CLASS.lower()}" %}}
Included section for class = {{{{yadm.class}}}} ({{{{yadm.class}}}} repeated)
Multiple lines
{{% else %}}
Should not be included...
{{% endif %}}
{{% if yadm.class == "{LOCAL_CLASS2.upper()}" %}}
Included section for second class
{{% endif %}}
{{% if yadm.class == "wrongclass2" %}}
wrong class 2
{{% endif %}}
{{% if yadm.arch == "wrongarch1" %}}
wrong arch 1
{{% endif %}}
{{% if yadm.arch == "{LOCAL_ARCH.title()}" %}}
Included section for arch = {{{{yadm.arch}}}} ({{{{yadm.arch}}}} repeated)
{{% endif %}}
{{% if yadm.arch == "wrongarch2" %}}
wrong arch 2
{{% endif %}}
{{% if yadm.os == "wrongos1" %}}
wrong os 1
{{% endif %}}
{{% if yadm.os == "{LOCAL_SYSTEM.lower()}" %}}
Included section for os = {{{{yadm.os}}}} ({{{{yadm.os}}}} repeated)
{{% endif %}}
{{% if yadm.os == "wrongos2" %}}
wrong os 2
{{% endif %}}
{{% if yadm.hostname == "wronghost1" %}}
wrong host 1
{{% endif %}}
{{% if yadm.hostname == "{LOCAL_HOST.upper()}" %}}
Included section for host = {{{{yadm.hostname}}}} ({{{{yadm.hostname}}}} again)
{{% endif %}}
{{% if yadm.hostname == "wronghost2" %}}
wrong host 2
{{% endif %}}
{{% if yadm.user == "wronguser1" %}}
wrong user 1
{{% endif %}}
{{% if yadm.user == "{LOCAL_USER.title()}" %}}
Included section for user = {{{{yadm.user}}}} ({{{{yadm.user}}}} repeated)
{{% endif %}}
{{% if yadm.user == "wronguser2" %}}
wrong user 2
{{% endif %}}
{{% if yadm.distro == "wrongdistro1" %}}
wrong distro 1
{{% endif %}}
{{% if yadm.distro == "{LOCAL_DISTRO.lower()}" %}}
Included section for distro = {{{{yadm.distro}}}} ({{{{yadm.distro}}}} again)
{{% endif %}}
{{% if yadm.distro == "wrongdistro2" %}}
wrong distro 2
{{% endif %}}
{{% if yadm.distro_family == "wrongfamily1" %}}
wrong family 1
{{% endif %}}
{{% if yadm.distro_family == "{LOCAL_DISTRO_FAMILY.upper()}" %}}
Included section for distro_family = \
{{{{yadm.distro_family}}}} ({{{{yadm.distro_family}}}} again)
{{% endif %}}
{{% if yadm.distro_family == "wrongfamily2" %}}
wrong family 2
{{% endif %}}
{{% if env.VAR == "{ENV_VAR.title()}" %}}
Included section for env.VAR = {{{{env.VAR}}}} ({{{{env.VAR}}}} again)
{{% endif %}}
{{% if env.VAR == "wrongenvvar" %}}
wrong env.VAR
{{% endif %}}
yadm.no_such_var="{{{{ yadm.no_such_var }}}}" and env.NO_SUCH_VAR="{{{{ env.NO_SUCH_VAR }}}}"
end of template
"""
EXPECTED = f"""
start of template
default class         = >{LOCAL_CLASS}<
default arch          = >{LOCAL_ARCH}<
default os            = >{LOCAL_SYSTEM}<
default host          = >{LOCAL_HOST}<
default user          = >{LOCAL_USER}<
default distro        = >{LOCAL_DISTRO}<
default distro_family = >{LOCAL_DISTRO_FAMILY}<
classes = >{LOCAL_CLASS2}
{LOCAL_CLASS}<
Included section from else
Included section from !=
Included section for class = {LOCAL_CLASS} ({LOCAL_CLASS} repeated)
Multiple lines
Included section for second class
Included section for arch = {LOCAL_ARCH} ({LOCAL_ARCH} repeated)
Included section for os = {LOCAL_SYSTEM} ({LOCAL_SYSTEM} repeated)
Included section for host = {LOCAL_HOST} ({LOCAL_HOST} again)
Included section for user = {LOCAL_USER} ({LOCAL_USER} repeated)
Included section for distro = {LOCAL_DISTRO} ({LOCAL_DISTRO} again)
Included section for distro_family = \
{LOCAL_DISTRO_FAMILY} ({LOCAL_DISTRO_FAMILY} again)
Included section for env.VAR = {ENV_VAR} ({ENV_VAR} again)
yadm.no_such_var="" and env.NO_SUCH_VAR=""
end of template
"""

INCLUDE_BASIC = "basic\n"
INCLUDE_VARIABLES = """\
included <{{ yadm.class }}> file ({{yadm.filename}})

empty line above
"""
INCLUDE_NESTED = "no newline at the end"

TEMPLATE_INCLUDE = """\
The first line
{% include empty %}
An empty file removes the line above
{%include ./basic%}
{% include "variables.{{ yadm.os }}"  %}
  {% include dir/nested %}
Include basic again:
{% include basic %}
"""
EXPECTED_INCLUDE = f"""\
The first line
An empty file removes the line above
basic
included <{LOCAL_CLASS}> file (VARIABLES_FILENAME)

empty line above
no newline at the end
Include basic again:
basic
"""

TEMPLATE_NESTED_IFS = """\
{% if yadm.user == "me" %}
    print1
  {% if yadm.user == "me" %}
    print2
  {% else %}
    no print1
  {% endif %}
{% else %}
  {% if yadm.user == "me" %}
    no print2
  {% else %}
    no print3
  {% endif %}
{% endif %}
{% if yadm.user != "me" %}
    no print4
  {% if yadm.user == "me" %}
    no print5
  {% else %}
    no print6
  {% endif %}
{% else %}
  {% if yadm.user == "me" %}
    print3
  {% else %}
    no print7
  {% endif %}
{% endif %}
"""
EXPECTED_NESTED_IFS = """\
    print1
    print2
    print3
"""


def test_template_default(runner, yadm, tmpdir):
    """Test template_default"""

    input_file = tmpdir.join("input")
    input_file.write(TEMPLATE, ensure=True)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join("output")

    # ensure overwrite works when file exists as read-only (there is some
    # special processing when this is encountered because some environments do
    # not properly overwrite read-only files)
    output_file.write("existing")
    output_file.chmod(0o400)

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        local_class="{LOCAL_CLASS}"
        local_classes=("{LOCAL_CLASS2}" "{LOCAL_CLASS}")
        local_arch="{LOCAL_ARCH}"
        local_system="{LOCAL_SYSTEM}"
        local_host="{LOCAL_HOST}"
        local_user="{LOCAL_USER}"
        local_distro="{LOCAL_DISTRO}"
        local_distro_family="{LOCAL_DISTRO_FAMILY}"
        template default "{input_file}" "{output_file}"
    """
    run = runner(command=["bash"], inp=script, env={"VAR": ENV_VAR})
    assert run.success
    assert run.err == ""
    assert output_file.read() == EXPECTED
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode


def test_source(runner, yadm, tmpdir):
    """Test yadm.source"""

    input_file = tmpdir.join("input")
    input_file.write("{{yadm.source}}", ensure=True)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join("output")

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        template default "{input_file}" "{output_file}"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert output_file.read().strip() == str(input_file)
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode


def test_include(runner, yadm, tmpdir):
    """Test include"""

    empty_file = tmpdir.join("empty")
    empty_file.write("", ensure=True)

    basic_file = tmpdir.join("basic")
    basic_file.write(INCLUDE_BASIC)

    variables_file = tmpdir.join(f"variables.{LOCAL_SYSTEM}")
    variables_file.write(INCLUDE_VARIABLES)

    nested_file = tmpdir.join("dir").join("nested")
    nested_file.write(INCLUDE_NESTED, ensure=True)

    input_file = tmpdir.join("input")
    input_file.write(TEMPLATE_INCLUDE)
    input_file.chmod(FILE_MODE)
    output_file = tmpdir.join("output")

    expected = EXPECTED_INCLUDE.replace("VARIABLES_FILENAME", str(variables_file))

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        local_class="{LOCAL_CLASS}"
        local_system="{LOCAL_SYSTEM}"
        template default "{input_file}" "{output_file}"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert output_file.read() == expected
    assert os.stat(output_file).st_mode == os.stat(input_file).st_mode


def test_nested_ifs(runner, yadm, tmpdir):
    """Test nested if statements"""

    input_file = tmpdir.join("input")
    input_file.write(TEMPLATE_NESTED_IFS, ensure=True)
    output_file = tmpdir.join("output")

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        local_user="me"
        template default "{input_file}" "{output_file}"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert output_file.read() == EXPECTED_NESTED_IFS


def test_env(runner, yadm, tmpdir):
    """Test env"""

    input_file = tmpdir.join("input")
    input_file.write("{{env.PWD}}", ensure=True)
    output_file = tmpdir.join("output")

    script = f"""
        YADM_TEST=1 source {yadm}
        set_awk
        template default "{input_file}" "{output_file}"
    """
    run = runner(command=["bash"], inp=script)
    assert run.success
    assert run.err == ""
    assert output_file.read().strip() == os.environ["PWD"]
