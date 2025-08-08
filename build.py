#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD_DIRS = [ROOT / "build", ROOT / "dist"]

for d in BUILD_DIRS:
    if d.exists():
        shutil.rmtree(d)

ICO = ROOT / "img" / "icon.ico"
ENTRY = ROOT / "app.py"   # 指向启动脚本
ADD_DATA = [
    (ROOT / "img", "img"),
    (ROOT / "src", "src"),
]

add_data_args = []
for src, dst in ADD_DATA:
    sep = ";" if os.name == "nt" else ":"
    add_data_args.extend(["--add-data", f"{src}{sep}{dst}"])

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--clean",
    "--noconfirm",
    "--name=lmdc",
    f"--icon={ICO}",
    "--version-file=version.txt",
    *add_data_args,
    str(ENTRY),
]

print(">>>", " ".join(str(x) for x in cmd))
subprocess.run(cmd, check=True)