#!/bin/env python3
"""
This application executes black on a file,
then pylint on the file,
and finally, auto-disables all issues that
pylint reports on that file.
"""
import click
import subprocess

# TODO: refactor to pass the file as an argument
FILE = "./yum_src.py"
PYLINTRC = "./pylintrc"


@click.version_option("0.1.0", prog_name="autoblack")
@click.command("main")
@click.option("-p", "--pylintrc", "pylintrc", type=click.File(mode="r"), default=None)
@click.option(
    "-t",
    "--target-version",
    "target_version",
    type=click.Choice(
        [
            "py33",
            "py34",
            "py35",
            "py36",
            "py37",
            "py38",
            "py39",
            "py310",
            "py311",
            "py312",
        ]
    ),
)
def main(pylintrc, target_version):
    execute_black(target_version)
    pylint_output = get_pylint_output(pylintrc)
    pylint_map = parse_pylint_out(pylint_output)
    autofix_file(pylint_map)


def get_pylint_output(pylintrc):
    try:
        output = subprocess.check_output(
            [
                "pylint",
                "--msg-template='{line:3d}:{symbol}'",
                "--rcfile",
                PYLINTRC,
                FILE,
            ],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        # when pylint finds errors, it returns non-zero code
        output = e.output
    return output


def autofix_file(pylint_map):
    if not bool(pylint_map):
        return
    with open(FILE, "r+", encoding="UTF8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line_num = str(i + 1)
            if line_num in pylint_map:
                new_line = (
                    f"{line.rstrip()} #  pylint: disable={pylint_map[line_num]}\n"
                )
                lines[i] = new_line
        f.seek(0)
        for line in lines:
            f.write(line)


def parse_pylint_out(pylint_out):
    res = {}
    for line in pylint_out.split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            num, err = line.split(":")
            if num in res:
                res[num] = f"{res[num]},{err}"
            else:
                res[num] = err
    return res


def execute_black(target_version):
    cmd = ["black", FILE]
    if target_version:
        cmd.extend(["-t", target_version])
    return subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )


if __name__ == "__main__":
    main()
