#!/bin/env python3
import os
import subprocess

FILE = "./yum_src.py"

def main():
    subprocess.Popen(f"black {FILE}", shell=True)


if __name__ == "__main__":
    main()