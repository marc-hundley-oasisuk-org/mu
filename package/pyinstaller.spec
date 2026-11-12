# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build specification for Mu Editor.

Build from the repository root with:
    pyinstaller --noconfirm --clean package/pyinstaller.spec

The first validation build deliberately enables the console. After the
application, modes, REPL and debugger have been tested, change console=True
below to console=False for the production GUI build.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

ROOT = Path(SPECPATH).resolve().parent

# Mu keeps runtime assets under the Python package, including resources,
# translations and bundled wheels. collect_data_files preserves their paths.
datas = collect_data_files("mu", include_py_files=False)

# The debugger launches mu_debug.py as a physical script using the
# Mu-managed Python runtime, so it must remain available outside
# PyInstaller's Python module archive.
datas.append(
    (
        str(ROOT / "mu" / "mu_debug.py"),
        "mu",
    )
)

# The student import policy is copied into Mu's managed Python environment
# at runtime, so preserve it as a physical source file outside PyInstaller's
# Python module archive.
datas.append(
    (
        str(ROOT / "mu" / "student_policy.py"),
        "mu",
    )
)

# mu_debug.py runs under Mu's separately managed Python environment.
# Package the debugger modules it imports as physical source files so
# they are available via the PYTHONPATH configured by Mu.
for debugger_file in (
    "config.py",
    "runner.py",
    "utils.py",
):
    datas.append(
        (
            str(ROOT / "mu" / "debugger" / debugger_file),
            "mu/debugger",
        )
    )

# Mu discovers or imports several mode/debugger components dynamically.
hiddenimports = []
for package_name in (
    "mu.modes",
    "mu.debugger",
    "mu.interface",
    "mu.resources",
    "mu.wheels",
):
    hiddenimports += collect_submodules(package_name)

# Jupyter Client discovers kernel provisioners dynamically through
# package entry points. Preserve both the provisioner implementations
# and their distribution metadata in the frozen application.
hiddenimports += collect_submodules("jupyter_client.provisioning")
datas += copy_metadata("jupyter_client")

# Qt components referenced by Mu and its pinned dependencies.
hiddenimports += [
    "PyQt5.Qsci",
    "PyQt5.QtChart",
    "PyQt5.QtSerialPort",
    "PyQt5.QtSvg",
]

# Use the Windows icon if it exists in the checked-out branch.
icon_candidates = (
    ROOT / "package" / "icons" / "mu.ico",
    ROOT / "package" / "icons" / "mu_icon.ico",
    ROOT / "package" / "icons" / "mu-editor.ico",
)

icon = next(
    (str(path) for path in icon_candidates if path.exists()),
    None,
)


base_python = Path(getattr(sys, "_base_executable", sys.executable)).resolve()
python_runtime = base_python.parent

a = Analysis(
    [str(ROOT / "run.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=sorted(set(hiddenimports)),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "sphinx",
        "twine",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="mu",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    icon=icon,
)

python_runtime_tree = Tree(
    str(python_runtime),
    prefix="python-runtime",
    excludes=["Doc"],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    python_runtime_tree,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="mu",
)