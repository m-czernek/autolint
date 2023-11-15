#!/bin/env python3
"""
This application executes black on a file,
then pylint on the file,
and finally, auto-disables all issues that
pylint reports on that file.
"""
import click
import subprocess
from pathlib import Path


@click.version_option("0.1.0", prog_name="autolint")
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
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        path_type=Path,
    ),
)
def main(paths, pylintrc, target_version):
    execute_black(paths, target_version)

    files = recursively_parse_files(paths)

    for file in files:
        pylint_output = get_pylint_output(pylintrc, file)
        pylint_map = parse_pylint_out(pylint_output)
        autofix_file(pylint_map, file)


def recursively_parse_files(paths):
    files = []
    for path in paths:
        if path.is_file():
            files.append(path)
            continue
        files.extend(path.rglob("*.py"))
    return files


def get_pylint_output(pylintrc, file):
    try:
        output = subprocess.check_output(
            [
                "pylint",
                "--msg-template='{line:3d}:{symbol}'",
                f"--rcfile {pylintrc}" if pylintrc else "",
                file,
            ],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        # when pylint finds errors, it returns non-zero code
        output = e.output
    return output


def autofix_file(pylint_map, file):
    if not bool(pylint_map):
        return
    with open(file, "r+", encoding="UTF8") as f:
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


def execute_black(paths, target_version):
    cmd = ["black"]
    if target_version:
        cmd.extend(["-t", target_version])
    cmd.extend(paths)

    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
