# Mu Python 3.15 Port - Progress Report & Build Notes
# 13/10/2026

## Overview

The objective was to take the archived open-source **Mu** editor and determine whether it could be modernised to run on a contemporary Python version while providing a foundation for future restrictions on imported modules.

The upstream project is archived, unmaintained, and officially targets Python 3.5-3.8. 【1-00cfcb】【2-a2d784】

### Result So Far

✅ Mu installs on Python 3.15

✅ Mu starts and displays the GUI

✅ PyQt5 loads successfully

✅ Resource loading has been modernised

✅ Startup reaches the main application

✅ Identified remaining issues in Mu's virtual-environment bootstrap subsystem

---

# Repository Setup

## Fork

Created a GitHub fork of:

```text
https://github.com/mu-editor/mu
```

The upstream repository is archived and read-only, so all future maintenance must occur in the fork. 【1-00cfcb】

---

# Python Version Modernisation

## Original Limitation

Mu explicitly restricted installation to:

```python
python_requires=">=3.5,<3.9"
```

which corresponds to the published support range in Mu's documentation. 【2-a2d784】

## Change Made

Updated package metadata to allow installation under Python 3.15.

Example:

```python
python_requires=">=3.5"
```

or a similar modernised range.

---

# Dependency Modernisation

## Original Dependencies

The project contained legacy versions such as:

```python
PyQt5==5.13.2
QScintilla==2.11.3
PyQtChart==5.13.1
jupyter-client<6.2
ipykernel<6
qtconsole==4.7.7
```

The maintainers had already identified these as blockers to newer Python support. 【3-e8abdf】【4-9a8b05】

## Updated Dependencies

Updated to modern versions:

```python
PyQt5>=5.15
QScintilla>=2.14
PyQtChart>=5.15
jupyter-client>=8
ipykernel>=6
qtconsole>=5
pyzmq>=26
```

This removed the majority of the installation problems.

---

# PyQt5-SIP Issue

## Problem

Old dependency:

```python
PyQt5-sip<=12.13.0
```

attempted to compile locally.

Result:

```text
Microsoft Visual C++ 14 required
```

## Resolution

Removed legacy SIP pinning and relied upon the current PyQt dependency chain.

Modern PyQt wheels install correctly.

---

# Resource Loading Migration

## Original Code

```python
from pkg_resources import (
    resource_filename,
    resource_string
)
```

Python 3.15 startup failed:

```text
ModuleNotFoundError:
pkg_resources
```

## Resolution

Replaced `pkg_resources` usage with direct filesystem access using:

```python
from pathlib import Path
```

Resource paths now resolve via:

```python
BASE_DIR = Path(__file__).parent
```

rather than setuptools resource APIs.

### Replacement Example

```python
from pathlib import Path

BASE_DIR = Path(__file__).parent

IMAGES_DIR = BASE_DIR / "images"
CSS_DIR = BASE_DIR / "css"
FONTS_DIR = BASE_DIR / "fonts"
```

This was the first source-code compatibility fix required for Python 3.15.

---

# User Settings Folder

## Problem

Mu expected:

```text
%LOCALAPPDATA%\python\mu
```

to exist.

Result:

```text
FileNotFoundError
```

## Resolution

Created:

```powershell
mkdir "$env:LOCALAPPDATA\python\mu"
```

or allow installer creation later.

---

# Wheels Download Subsystem

## Discovery

After startup issues were resolved, Mu reached:

```text
virtual_environment.py
```

and attempted to create its internal educational virtual environment.

This uses:

```text
mu/wheels/__init__.py
```

to download predefined packages.

---

# Error Handler Bug Found

## Original Code

```python
"Pip was unable to download %s" % pip_identifiers
```

Produced:

```text
TypeError:
not all arguments converted during string formatting
```

when multiple package identifiers were supplied.

## Fixed Version

```python
raise WheelsDownloadError(
    f"Pip was unable to download {pip_identifiers}"
)
```

This exposed the real failure.

---

# Pygame / PGZero Failure

Mu attempted to install:

```text
pgzero>=1.2.1
pygame<2.1.3
```

during startup.

The error initially appeared to be a dependency compatibility problem.

However, after fixing logging, the true cause was revealed:

```text
SSL: CERTIFICATE_VERIFY_FAILED
```

during package download.

---

# Real Root Cause

The real failure was:

```text
urllib.error.URLError:
[SSL: CERTIFICATE_VERIFY_FAILED]
certificate verify failed:
unable to get local issuer certificate
```

Therefore:

### Root Cause

Not Mu.

Not Python 3.15.

Instead:

```text
TLS certificate validation problem
```

inside the Windows Sandbox environment.

---

# Current Working State

To verify the editor itself works, virtual environment creation was temporarily bypassed.

Location:

```python
mu/app.py
```

Original:

```python
venv.ensure_and_create(self.display_text)
```

Temporary workaround:

```python
# venv.ensure_and_create(self.display_text)
```

Result:

✅ Mu launches

✅ GUI loads

✅ Splash screen completes

✅ Python 3.15 runtime functional

This proves the editor itself is portable.

---

# Recommended Future Improvements

## Complete Resource Migration

Replace all remaining:

```python
pkg_resources
```

references with:

```python
importlib.resources
```

or

```python
pathlib
```

based implementations.

---

## Modernise Wheel Package Definitions

Update wheel bootstrap packages:

### Old

```python
pgzero>=1.2.1
pygame<2.1.3
```

### Proposed

```python
pgzero
pygame>=2.6
```

after compatibility testing.

---

## Fix SSL Handling

Potential options:

### Option 1

Install proper root certificates into Windows Sandbox.

### Option 2

Pre-package wheel files during installer creation.

### Option 3

Remove runtime wheel downloads entirely.

For managed educational deployments, Option 3 is recommended.

---

# Restricting Imports (Future Work)

The original objective remains fully achievable.

## Static Validation

Before execution:

```python
import ast
```

Parse imports and compare against an allow-list.

Example:

```python
ALLOWED = {
    "math",
    "random",
    "datetime",
    "turtle",
}
```

---

## Runtime Validation

Override imports inside the execution environment:

```python
import builtins

_original_import = builtins.__import__

def restricted_import(name, *args, **kwargs):
    root = name.s***t(".")[0]

    if root not in AL***ED:
        raise ImportError(
 ***        f"{root} not permitted"
***     )

    return _original_imp***(
        name,
        *args,
 ***    **kwargs
    )

builtins.__i***rt__ = restricted_import
```

--***# Important Design Principle

Do***not** remove:

```python
os
sys
***process
pathlib
```

from Mu its***.

Mu internally depends on many*** these modules.

Restrict them o*** in the interpreter that execute***ser code.

---

# Newer Mu Versi***Investigation

During crash hand***g Mu reports:

```text
There is ***ewer version of Mu available
```***owever the archived GitHub repos***ry remains at version 1.2.2. 【1-00cfcb】【2-a2d784】

This suggests on***f:

1. The update URL is hardcod***
2. A release exists outside Git***.
3. A post-GitHub packaged rele*** was produced.
4. The update-che***endpoint was never updated.

## ***ure Investigation

Inspect:

```***t
mu/logic.py
mu/app.py
mu/versi***py
```

Search for:

```powershe***findstr /S /I "codewith.mu" *.py***ndstr /S /I "latest version" *.p***indstr /S /I "download" *.py
```***etermine how update checking is ***formed.

---

# Building a Windo***Installer

## Recommended Build ***cess

### Step 1

Get the applic***on fully stable.

### Step 2

Cr***e a release tag:

```powershell
*** tag v1.3.0-custom
git push --ta***```

### Step 3

Create a standa***e executable using PyInstaller:
***`powershell
pip install pyinstal***
```

Build:

```powershell
pyin***ller run.py --name MuCustom
```
***tput:

```text
dist\
```

---

#***eate EXE Installer

## Option A ***nno Setup (Recommended)

Generat***
```text
MuCustomSetup.exe
```

***antages:

- Easy to maintain
- W***ly supported
- Small installer
-***itable for schools

---

# Creat***SI Installer

## Option B - WiX ***lset

Generate:

```text
MuCusto***si
```

Advantages:

- Enterpris***eployment
- Intune compatible
- ***M compatible
- Group Policy depl***ent

For education and enterpris***eployment, MSI via WiX is the preferred long-term option.

---

# Suggested Packaging Architecture

```text
Mu-Education
│
├── Python 3.15
├── Import Allow List
├── Restricted Runtime
├── Modernised Dependencies
├── Custom Branding
├── MSI Installer
└── Intune/GPO Deployment Support
```

---

# Current Project Status

| Area | Status |
|--------|--------|
| Python 3.15 installation | ✅ |
| Dependency upgrades | ✅ |
| PyQt5 upgrade | ✅ |
| QScintilla upgrade | ✅ |
| Resource loading fix | ✅ |
| GUI startup | ✅ |
| Virtual environment bootstrap | ⚠ Needs work |
| Wheel package definitions | ⚠ Needs modernisation |
| SSL handling | ⚠ Environment-specific |
| Import restrictions | ❌ Not implemented |
| MSI/EXE packaging | ❌ Not implemented |
| Python 3.15 viability | ✅ Proven |

---

# Summary

The most important conclusion is:

> **Mu itself appears capable of running on Python 3.15 with a relatively small number of code changes.**

The remaining issues are primarily:

1. Virtual-environment bootstrap modernisation.
2. Runtime package download handling.
3. Installer creation.
4. Student-code import restrictions.

The core application, GUI, Qt framework, and editor functionality have already been demonstrated to work under Python 3.15.