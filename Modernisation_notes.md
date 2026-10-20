# Mu Modernisation Notes

## Purpose

This fork is modernising Mu for continued use with Python 3.15 and a reproducible Windows deployment process.

The current development branch is:

```text
python315
```

Python 3.15.0 is an intentional runtime requirement.

The objective is not simply to make Mu launch. The target is a reproducible Windows build in which the editor, Python execution environment, REPL and debugger operate correctly.

---

## Current status

### Source application

| Component | Status |
|---|---|
| Mu application launch | PASS |
| Python 3.15 development environment | PASS |
| Mu-managed runtime creation | PASS |
| Runtime Python 3.15 | PASS |
| Runtime pip provisioning | PASS |
| Editor | PASS |
| File operations | PASS |
| Run Python | PASS |
| Debugger bootstrap | PASS |
| Breakpoints/debugging | PASS |
| REPL | FAIL / under investigation |

The source application is substantially functional but is not yet considered fully validated for Python 3.15.

---

## Development environment

Current development baseline:

- Windows 11
- Python 3.15.0
- Repository-local `.venv`
- Git
- VS Code
- PowerShell

Mu can be launched from the repository root with:

```powershell
.\.venv\Scripts\python.exe .\run.py
```

---

## Mu runtime architecture

Mu uses two separate Python environments.

### Development/application environment

The repository development environment is:

```text
<repository>\.venv
```

This environment runs Mu itself during source development.

### Mu-managed user runtime

Mu separately creates a runtime under the user's local application data directory.

Conceptually:

```text
%LOCALAPPDATA%\python\mu\mu_venv-315-<timestamp>
```

User Python programs, debugger components and other Python-mode functionality rely on this environment.

This distinction is important. A healthy development `.venv` does not prove that Mu's own runtime provisioning is working.

---

## Runtime provisioning restoration

Mu's normal startup provisioning had previously been disabled in `mu/app.py`.

The expected call is:

```python
venv.ensure_and_create(self.display_text)
```

Restoring this exposed the actual Python 3.15 compatibility issues in Mu's runtime provisioning process.

The runtime creation path is approximately:

```text
ensure_and_create()
    |
    +-- create()
    |   |
    |   +-- create_venv()
    |   +-- upgrade_runtime_pip()
    |   +-- install_baseline_packages()
    |   +-- register_baseline_packages()
    |   +-- install_jupyter_kernel()
    |
    +-- ensure()
```

---

## pip compatibility

The version of `virtualenv` used during development initially seeded:

```text
pip 23.1
```

into the Mu-managed Python 3.15 runtime.

That version of pip failed under Python 3.15 when processing wheels, including errors involving `WheelDistribution`.

Python 3.15's bundled `ensurepip` was tested and successfully upgraded the runtime to:

```text
pip 26.2.1
```

Mu now upgrades the runtime pip immediately after creating the virtual environment.

The bootstrap uses:

```text
python -I -m ensurepip --upgrade --default-pip
```

`--default-pip` is required because Mu expects:

```text
Scripts\pip.exe
```

Without that option, Python generated versioned launchers such as:

```text
pip3.exe
pip3.15.exe
```

but no unqualified `pip.exe`.

---

## Pygame and Python 3.15

The original runtime provisioning requests upstream `pygame`.

The upstream package selected during testing was `pygame 2.6.1`. No compatible Windows CPython 3.15 wheel was selected, causing pip to fall back to a source distribution.

The source build subsequently attempted to retrieve SDL build dependencies and failed during certificate validation.

This source-build path is not suitable for the managed estate deployment.

### pygame-ce

`pygame-ce 2.5.8` was validated with Python 3.15.

A native Windows CPython 3.15 wheel was successfully retrieved:

```text
pygame_ce-2.5.8-cp315-cp315-win_amd64.whl
```

It was installed successfully and exposes the expected import:

```python
import pygame
```

The current baseline therefore uses:

```text
pygame-ce>=2.5.8
```

---

## Pygame Zero dependency handling

The metadata from the `pgzero 1.2.1` wheel declares:

```text
pygame ~=2.0
numpy
enum34 ; python_version < "3.4"
```

Although `pygame-ce` exposes the `pygame` module, its distribution name does not satisfy the `pygame~=2.0` package dependency.

Without intervention, pip attempted to install both:

```text
pygame-ce
pygame
```

The latter returned provisioning to the unsupported Pygame source-build path.

For the controlled Mu baseline, Pygame Zero dependencies are explicitly supplied and automatic dependency resolution is disabled for this group.

The Python 3.15 baseline explicitly includes:

```text
pgzero>=1.2.1
pygame-ce>=2.5.8
numpy
```

`enum34` does not apply to Python 3.15.

---

## Source validation achieved

After applying the runtime pip and Pygame Zero dependency changes, Mu successfully:

- built the managed Python 3.15 runtime;
- launched from source;
- ran Python code;
- opened and saved files;
- started the debugger;
- reached breakpoints and completed debugger testing.

This is a suitable committed checkpoint before addressing the REPL separately.

---

## Debugger

Manual testing established that Mu's debugger server can run under Python 3.15 and listen on its configured localhost port.

Following the runtime provisioning fixes, debugger operation from Mu has been successfully validated.

Validated:

- debugger bootstrap;
- debugger connection;
- breakpoint/debug operation.

### `bp_index` robustness issue

A separate robustness issue has been identified in the debugger client.

`mu/debugger/client.py` accesses:

```python
self.bp_index
```

before that member is guaranteed to have been initialised by debugger bootstrap.

This previously produced:

```text
AttributeError: 'Debugger' object has no attribute 'bp_index'
```

This issue should remain separate from the runtime provisioning work and should only be modified if it remains reproducible during subsequent validation.

---

## REPL

The REPL remains the principal known Python 3.15 issue.

The source application can now create its managed runtime and the debugger is operational, significantly narrowing the REPL investigation.

REPL work should be performed as a separate change from the completed runtime provisioning remediation.

Target validation:

```text
REPL starts
kernel is located
kernel starts
input executes
output returns to Mu
REPL closes cleanly
```

The crash report and log from the latest REPL test should be treated as the next primary evidence source.

---

## PyInstaller Windows packaging

The original packaging documentation referenced a `pyinstaller.spec` that was no longer present.

A maintained packaging implementation has been added:

```text
package\
    prepare-pyinstaller.ps1
    pyinstaller.spec
    PYINSTALLER_BUILD.rst
```

PyInstaller has successfully completed a Windows build using Python 3.15.

The resulting executable is:

```text
dist\mu\mu.exe
```

Previous packaging validation established:

```text
PyInstaller Analysis       PASS
PYZ                        PASS
PKG                        PASS
EXE                        PASS
COLLECT                    PASS
Mu executable launch       PASS
Qt UI                      PASS
Editor                     PASS
Python execution           PASS
File operations            PASS
```

That build pre-dated completion of the current runtime-provisioning remediation.

The packaged application must therefore be rebuilt and revalidated after source-level Python 3.15 validation is complete.

See:

```text
package\PYINSTALLER_BUILD.rst
```

---

## Windows packaging workflow

From the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\package\prepare-pyinstaller.ps1
.\.venv\Scripts\python.exe .\run.py
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean .\package\pyinstaller.spec
.\dist\mu\mu.exe
```

The current build is intentionally a PyInstaller one-directory build. The full `dist\mu` directory is required for distribution and testing.

Do not move to a one-file build until the one-directory build is stable and fully validated.

---

## Git and generated content

Source and build configuration should be retained in Git.

Tracked examples:

```text
package\pyinstaller.spec
package\prepare-pyinstaller.ps1
package\PYINSTALLER_BUILD.rst
```

Generated content should not be committed.

Ignored/generated examples:

```text
.venv\
build\
dist\
__pycache__\
*.pyc
```

Mu-generated runtime environments beneath `%LOCALAPPDATA%` are runtime state and are not repository content.

The generated baseline file `mu\wheels\1.2.2.zip` should be reviewed deliberately before committing. It should not be committed automatically merely because a successful local provisioning run created it.

---

## Validation strategy

Modernisation work should continue using this controlled sequence:

1. Establish the baseline.
2. Reproduce the issue.
3. Inspect the actual failure.
4. Identify the root cause.
5. Make one targeted change.
6. Validate from source.
7. Commit the validated change.
8. Rebuild packaging only when the source application is stable.

Avoid combining unrelated compatibility fixes into the same commit.

---

## Current next priority

The next primary investigation is the Python 3.15 REPL failure.

Do not begin final PyInstaller validation until the source validation matrix is complete.

Target source state:

```text
Application launch       PASS
Runtime environment      PASS
Editor                   PASS
Run Python               PASS
File operations          PASS
REPL                     PENDING
Debugger bootstrap       PASS
Breakpoint/debugging     PASS
```

Once the REPL passes, rebuild and validate the Windows distributable.
