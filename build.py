import os
import subprocess
import shutil

def install():
    subprocess.run(["pip", "install", "-e", ".[dev]"])

def build():
    subprocess.run(["pyinstaller", "LaserDeMag.spec"])

def run():
    subprocess.run(["python", "-m", "LaserDeMag.main"])

def docs():
    subprocess.run(["pdoc", "LaserDeMag", "-o", "docs", "--force"])

def clean():
    for folder in ["dist", "build", "docs", "__pycache__"]:
        shutil.rmtree(folder, ignore_errors=True)
    for file in ["LaserDeMag.spec"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    import sys
    actions = {
        "install": install,
        "build": build,
        "run": run,
        "docs": docs,
        "clean": clean,
    }
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        print("Use: python build.py [install|build|run|docs|clean]")
    else:
        actions[sys.argv[1]]()
