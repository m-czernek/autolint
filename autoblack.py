#!/bin/env python3
import os
import subprocess
import sys

FILE = "./yum_src.py"
PYLINTRC = "./pylintrc"

def main():
    with open("out.log", "w", encoding="UTF8") as f:
        #execute_cmd(["black", FILE], f)
        pass
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
            if i + 1 in pylint_map:
                line = f"{line} #  pylint: disable={pylint_map[i+1]}"
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
