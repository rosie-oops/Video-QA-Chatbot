"""
1. Read requirements.txt
2. Check whether each package is already installed
3. If anything is missing, run `pip install -r requirements.txt`
4. Launches the Streamlit app (app.py)
"""



import importlib.metadata
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(SCRIPT_DIR, "requirements.txt")
APP_FILE = os.path.join(SCRIPT_DIR, "app.py")


def _read_text_auto_encoding(path: str) -> str:
   
    with open(path, "rb") as f:
        raw = f.read()

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    return raw.decode("utf-8")


def _parse_requirements(path: str) -> list[str]:

    packages = []
    text = _read_text_auto_encoding(path)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        name = re.split(r"[=<>~!\[]", line, maxsplit=1)[0].strip()
        if name:
            packages.append(name)
    return packages


def _is_installed(package_name: str) -> bool:
    try:
        importlib.metadata.distribution(package_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def check_and_install_requirements():
    print("Checking requirements...")
    packages = _parse_requirements(REQUIREMENTS_FILE)

    missing = [pkg for pkg in packages if not _is_installed(pkg)]

    if not missing:
        print("All requirements already installed.")
        return

    print(f"Missing packages: {', '.join(missing)}")
    print("Installing from requirements.txt ...")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE]
    )

    if result.returncode != 0:
        print("pip install failed. Please check the error above and try again.")
        sys.exit(1)

    print("Requirements installed successfully.")


def launch_app():
    print("Launching Streamlit app...")
    subprocess.run(["streamlit", "run", APP_FILE], cwd=SCRIPT_DIR)


if __name__ == "__main__":
    check_and_install_requirements()
    launch_app()