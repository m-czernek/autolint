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
@click.option("-p", "--pylintrc", "pylintrc", default=None, type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        path_type=Path,
    ))
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
#    execute_black(paths, target_version)

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
    cmd = [
                "pylint",
                "--msg-template='{line:3d}:{symbol}'",
                f"--rcfile {pylintrc}" if pylintrc else "",
                file,
            ]
    try:
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        # when pylint finds errors, it returns non-zero code
        output = e.output
    return output


def autofix_file(pylint_map, file):
    if not bool(pylint_map):
        print(f"Empty map for {file}, returning")
        return
    try:
        with open(file, "r+", encoding="UTF-8") as f:
            lines = f.readlines()
            for line_num,pylint_val in sorted(pylint_map.items(), key=lambda kv:int(kv[0]), reverse=True):
                # arrays are 0-indexed, pylint-out is 1-indexed
                line_num_i = int(line_num) - 1
                curr_line = lines[line_num_i]
                num_of_spaces = len(curr_line) - len(curr_line.lstrip())
                new_line = ''.rjust(num_of_spaces)
                new_line = f"{new_line}#  pylint: disable-next={pylint_val}\n"
                if line_num_i == 0:
                    new_line = new_line.replace("-next", "")
                lines.insert(line_num_i, new_line)
            f.seek(0)
            for line in lines:
                f.write(line)
    except Exception as e:
        print(f"Could not fix {file}")
        print(e)


def parse_pylint_out(pylint_out):
    res = {}
    for line in pylint_out.split("\n"):
        line = line.strip()
        if line and line[0].isdigit() and 'fatal' not in line:
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
