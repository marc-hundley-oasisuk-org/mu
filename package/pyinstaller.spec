# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build specification for Mu Editor.

Build from the repository root with:
    pyinstaller --noconfirm --clean package/pyinstaller.spec

The first validation build deliberately enables the console. After the
application, modes, REPL and debugger have been tested, change console=True
below to console=False for the production GUI build.
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).resolve().parent

# Mu keeps runtime assets under the Python package, including resources,
# translations and bundled wheels. collect_data_files preserves their paths.
datas = collect_data_files("mu", include_py_files=False)

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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="mu",
)