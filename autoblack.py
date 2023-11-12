#!/bin/env python3
import subprocess

FILE = "./yum_src.py"
PYLINTRC = "./pylintrc"

def main():
    output = None
    try:
        output = subprocess.check_output([
            "pylint",
            "--msg-template='{line:3d}:{symbol}'",
            "--rcfile",
            PYLINTRC,
            FILE
        ], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        output = e.output

    pylint_map = parse_pylint_out(output)
    autofix_file(pylint_map)

def autofix_file(pylint_map):
    if not bool(pylint_map):
        return
    with open(FILE, "r+", encoding="UTF8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line_num = str(i + 1)
            if line_num in pylint_map:
                new_line = f"{line.rstrip()} #  pylint: disable={pylint_map[line_num]}\n"
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



def execute_cmd(cmd, out_f):
    return subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=out_f
    )

if __name__ == "__main__":
    main()
