# Mu Modernisation Notes

## Purpose

This fork modernises Mu for continued use with mandatory Python 3.15 and a reproducible Windows deployment process.

The stable repository branch is:

```text
main
```

Current student import-policy development is being performed on:

```text
student-import-policy
```

The previous:

```text
python315
```

branch remains available as a historical/recovery reference but is no longer the active development baseline.

Python 3.15.0 is an intentional runtime requirement.

The objective is not simply to make Mu launch. The target is a reproducible Windows build in which the editor, Python execution environment, REPL, debugger and curriculum import policy operate correctly.

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
| Breakpoints | PASS |
| Step / Continue | PASS |
| REPL | PASS |
| REPL close / reopen | PASS |
| Clean shutdown with active REPL | PASS |
| Student import policy | PASS |

The source application is fully functional for the currently validated Python 3.15 baseline.

### Packaged application

The current PyInstaller one-directory build has also been validated for:

- application startup;
- managed Python 3.15 provisioning;
- Run;
- Debug;
- breakpoints;
- Step;
- Continue;
- REPL;
- REPL close and reopen;
- clean shutdown;
- student import-policy provisioning;
- student import-policy enforcement across Run, Debug and REPL.

---

## Development environment

Current development baseline:

- Windows 11
- Python 3.15.0
- repository-local `.venv`
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

User Python programs, debugger components and Python-mode REPL functionality rely on this environment.

This distinction is important. A healthy development `.venv` does not prove that Mu's own runtime provisioning is working.

---

## Runtime provisioning restoration

Mu's normal startup provisioning had previously been disabled in `mu/app.py`.

The expected call is:

```python
venv.ensure_and_create(self.display_text)
```

Restoring this exposed the Python 3.15 compatibility issues in Mu's runtime provisioning process.

The current creation path is approximately:

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
    |   +-- install_student_policy()
    |
    +-- ensure()
        |
        +-- ensure_path()
        +-- ensure_interpreter()
        +-- ensure_interpreter_version()
        +-- ensure_pip()
        +-- ensure_key_modules()
        +-- install_student_policy()
```

The policy provisioning step also runs during validation of an existing managed environment, allowing an existing valid runtime to receive an updated policy without requiring recreation.

---

## Python 3.15 managed environment

Managed-runtime creation now uses Python's standard-library `venv` implementation.

Do not revert this to third-party `virtualenv` creation.

When running from source, the development Python interpreter acts as the base interpreter.

When running from the packaged application, Mu uses:

```text
dist\mu\_internal\python-runtime\python.exe
```

as the base interpreter.

Student Python ultimately executes from the separately managed per-user environment rather than from PyInstaller's `mu.exe`.

---

## pip compatibility

The version of `virtualenv` used during early development initially seeded:

```text
pip 23.1
```

into the Mu-managed Python 3.15 runtime.

That version of pip failed under Python 3.15 when processing wheels, including errors involving `WheelDistribution`.

Python 3.15's bundled `ensurepip` was validated as the replacement bootstrap mechanism.

Mu upgrades runtime pip immediately after creating the managed environment.

The bootstrap uses:

```text
python -I -m ensurepip --upgrade --default-pip
```

`--default-pip` is required because Mu expects:

```text
Scripts\pip.exe
```

Without that option, Python can generate versioned launchers without the unqualified `pip.exe`.

---

## Pygame and Python 3.15

The original runtime provisioning requested upstream `pygame`.

During testing, upstream `pygame 2.6.1` did not provide the required Windows CPython 3.15 installation path and provisioning fell back to a source build.

The source-build path was unsuitable for the managed deployment.

### pygame-ce

`pygame-ce 2.5.8` was validated with Python 3.15.

A Windows CPython 3.15 wheel was successfully retrieved:

```text
pygame_ce-2.5.8-cp315-cp315-win_amd64.whl
```

It exposes the expected import:

```python
import pygame
```

The current baseline therefore uses:

```text
pygame-ce>=2.5.8
```

---

## Pygame Zero dependency handling

The metadata from `pgzero 1.2.1` declares:

```text
pygame ~=2.0
numpy
enum34 ; python_version < "3.4"
```

Although `pygame-ce` exposes the `pygame` module, its distribution name does not satisfy the `pygame~=2.0` distribution dependency.

For the controlled Mu baseline, Pygame Zero dependencies are therefore explicitly supplied and automatic dependency resolution is disabled for this group.

The Python 3.15 baseline explicitly includes:

```text
pgzero>=1.2.1
pygame-ce>=2.5.8
numpy
```

`enum34` does not apply to Python 3.15.

---

## Debugger

The Mu debugger is operational under Python 3.15.

Validated:

- debugger bootstrap;
- debugger connection;
- breakpoints;
- Step;
- Continue;
- normal output;
- clean termination;
- student import-policy enforcement.

The debugger uses Mu's managed Python interpreter.

When packaged, physical debugger files are retained beneath:

```text
dist\mu\_internal\mu\
```

The external debugger bootstrap requires:

```text
mu_debug.py
mu\debugger\config.py
mu\debugger\runner.py
mu\debugger\utils.py
```

The managed runtime does not contain Mu itself by design, so debugger launch temporarily provides Mu's source/package path through `PYTHONPATH`.

### `bp_index` robustness issue

A separate historical robustness issue was identified in the debugger client where `self.bp_index` could be referenced before initialisation.

This is not currently part of the active Python 3.15 or import-policy work.

Do not modify this area without new reproducible evidence.

---

## REPL

The Python 3.15 REPL is operational.

Validated in both source and packaged Mu:

```text
REPL starts
kernel is located
kernel starts
input executes
output returns to Mu
REPL closes
REPL reopens
reopened REPL executes
clean application exit with active REPL
```

The REPL uses the managed Python environment and Jupyter/IPython stack.

Current validated components include:

```text
ipykernel 7.4.0
IPython 9.17.1
Jupyter QtConsole 5.7.2
```

A previous failure involving REPL shutdown and QThread lifecycle was resolved during the Python 3.15 modernisation work.

The working QThread lifecycle must not be changed without new reproducible evidence.

---

## Student Python import policy

A curriculum-focused import allow-list has been implemented for Python 3 mode.

The educational requirement is to expose only the library modules required by the curriculum while reducing straightforward student access to unnecessary system-facing Python modules.

### Allowed student imports

The initial allow-list is:

```text
math
random
time
turtle
```

These are defined centrally in:

```text
mu\student_policy.py
```

### Policy scope

The policy applies consistently to:

- Run;
- Debug;
- REPL.

It handles:

```python
import module
```

```python
from module import member
```

and explicit dynamic imports such as:

```python
__import__("module")
```

Top-level module names are used for policy evaluation.

### Context-sensitive enforcement

A simple global import deny-list was deliberately not used.

Permitted modules can depend internally on modules that students are not permitted to import directly.

For example:

```text
student code
    |
    +-- import turtle          ALLOWED
            |
            +-- tkinter       INTERNAL - ALLOWED
            +-- pathlib       INTERNAL - ALLOWED
            +-- os            INTERNAL - ALLOWED
            +-- sys           INTERNAL - ALLOWED
```

while:

```text
student code
    |
    +-- import os              BLOCKED
```

The policy therefore determines whether the import originates from student execution before enforcing the allow-list.

### Student execution contexts

Normal Run and Debug student code execute as:

```text
__name__ == "__main__"
```

with the student file represented by `__file__`.

The Jupyter REPL executes student-entered commands as:

```text
__name__ == "__main__"
__file__ == None
```

Known infrastructure launchers including:

```text
mu_debug.py
ipykernel_launcher.py
```

are excluded from student-context treatment.

Imports initiated by Mu infrastructure, Python standard-library modules, Jupyter/IPython and dependencies of allowed curriculum modules therefore remain unrestricted.

### Environment activation

Enforcement is additionally gated by:

```text
MU_STUDENT_IMPORT_POLICY=1
```

Both conditions must be satisfied:

```text
policy enabled
      AND
student import context
       |
       v
enforce allow-list
```

If the environment variable is absent, the installed hook passes imports through normally.

This keeps the following unrestricted:

- managed-environment creation;
- `ensurepip`;
- pip;
- baseline package installation;
- baseline package validation;
- Jupyter registration;
- Mu infrastructure imports.

Mu enables the policy only for student:

- Run;
- Debug;
- REPL.

### Managed-runtime deployment

The managed environment does not contain the Mu package itself.

Mu therefore provisions the policy into the managed interpreter's `purelib` location as:

```text
Lib\site-packages\mu_student_policy.py
```

and creates:

```text
Lib\site-packages\sitecustomize.py
```

The `sitecustomize.py` bootstrap installs the import hook whenever the managed interpreter starts.

Enforcement still depends on `MU_STUDENT_IMPORT_POLICY=1`.

### PyInstaller deployment

`package\pyinstaller.spec` explicitly preserves:

```text
mu\student_policy.py
```

as a physical data file.

The expected packaged location is:

```text
dist\mu\_internal\mu\student_policy.py
```

This physical source is used to provision the managed Python environment.

The following three policy representations have been confirmed as content-equivalent:

```text
repository mu\student_policy.py
packaged dist\mu\_internal\mu\student_policy.py
managed Lib\site-packages\mu_student_policy.py
```

Raw SHA256 values may differ when Windows text processing changes LF/CRLF line endings. Normalised content comparison has been confirmed identical.

### Validation

Automated policy tests are maintained in:

```text
tests\test_student_policy.py
```

Focused policy test result:

```text
38 passed
```

The tests cover:

- allow-list classification;
- deny behaviour;
- top-level module handling;
- environment activation;
- Run context classification;
- Debug/infrastructure classification;
- REPL context classification;
- import-hook installation;
- import-hook removal;
- normal import statements;
- from-import statements;
- explicit `__import__()` calls;
- permitted dynamic imports;
- `turtle` transitive dependencies.

A full Mu test run during development produced:

```text
1151 passed
20 skipped
7 failed
```

The seven failures occurred outside the new student-policy tests and related to existing test expectations in other modernised areas.

The student-policy tests themselves passed as part of the full randomised test run.

### Functional validation

Source and packaged Mu have both been manually validated.

| Behaviour | Run | Debug | REPL |
|---|---|---|---|
| `math` | PASS | PASS | PASS |
| `random` | PASS | PASS | PASS |
| `time` | PASS | PASS | PASS |
| `turtle` | PASS | PASS | PASS |
| prohibited module import | BLOCK | BLOCK | BLOCK |
| prohibited `from ... import ...` | BLOCK | BLOCK | BLOCK |
| prohibited `__import__()` | BLOCK | BLOCK | BLOCK |
| permitted transitive imports | PASS | PASS | PASS |

Debugger validation additionally confirms:

- breakpoint;
- Step;
- Continue.

REPL validation additionally confirms:

- expression execution;
- close;
- reopen;
- clean shutdown.

### Security boundary

The student import policy is a curriculum restriction and defence-in-depth control.

It is not intended to provide a complete Python security sandbox.

The policy reduces directly accessible modules and blocks straightforward import routes, but Windows endpoint controls remain the device security boundary.

Relevant endpoint protections include:

- standard-user permissions;
- application control;
- endpoint protection;
- network controls;
- other estate security configuration.

---

## PyInstaller Windows packaging

The maintained packaging implementation is:

```text
package\
    prepare-pyinstaller.ps1
    pyinstaller.spec
    PYINSTALLER_BUILD.md
```

PyInstaller successfully completes a Windows one-directory build using Python 3.15.

The resulting executable is:

```text
dist\mu\mu.exe
```

The current packaged build has passed:

```text
PyInstaller Analysis          PASS
PYZ                           PASS
PKG                           PASS
EXE                           PASS
COLLECT                       PASS
Mu executable launch          PASS
Managed runtime provisioning  PASS
Qt UI                         PASS
Editor                        PASS
Python Run                    PASS
Debugger                      PASS
REPL                          PASS
Student import policy         PASS
Clean shutdown                PASS
```

### Packaging metadata repair

The root repository contains:

```text
README.md
```

rather than the historical:

```text
README.rst
```

`setup.py` has therefore been corrected to use `README.md` for its long description with:

```text
text/markdown
```

content type.

### Build preparation

`package\prepare-pyinstaller.ps1` has been hardened to check the exit code of critical native package-management commands.

The script now fails instead of incorrectly reporting a prepared environment after a failed pip operation.

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

The current build is intentionally a PyInstaller one-directory build.

The full:

```text
dist\mu
```

directory is required for distribution and testing.

Do not move to a one-file build without separate controlled validation.

---

## Runtime payload optimisation

The full bundled Python 3.15 installation was originally approximately:

```text
185.05 MB
```

The largest removable component identified was:

```text
Doc\    78.73 MB
```

`Doc\` was excluded from the PyInstaller Python runtime `Tree`.

The resulting bundled Python runtime is approximately:

```text
106.32 MB
```

for a saving of approximately:

```text
78.73 MB
```

The complete functional validation matrix passed after this change.

Further aggressive trimming deliberately stopped.

Although components such as `Lib\test` remain comparatively large, the current approximately 106 MB bundled runtime is acceptable.

Do not continue runtime-size optimisation without a clear deployment requirement.

---

## Git and generated content

Source and build configuration should be retained in Git.

Tracked examples include:

```text
mu\student_policy.py
tests\test_student_policy.py
package\pyinstaller.spec
package\prepare-pyinstaller.ps1
package\PYINSTALLER_BUILD.md
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

The generated baseline file:

```text
mu\wheels\1.2.2.zip
```

should not be committed automatically merely because a successful local provisioning run created it.

---

## Validation strategy

Modernisation work should continue using this controlled sequence:

1. Inspect the current implementation.
2. Establish the existing behaviour.
3. Reproduce the issue or requirement.
4. Identify the root cause or architecture.
5. Make one targeted change.
6. Validate the change.
7. Commit a recovery point.
8. Progress to the next isolated change.

Avoid combining unrelated compatibility fixes into the same commit.

For packaging changes:

```text
source validation
    ->
clean PyInstaller build
    ->
packaged validation
```

should remain mandatory.

---

## Current project baseline

The Python 3.15 modernisation and Windows PyInstaller implementation are functionally complete for the currently validated scope.

Current status:

```text
Application launch             PASS
Python 3.15 managed runtime    PASS
Runtime pip                    PASS
Editor                         PASS
File operations                PASS
Run Python                     PASS
Debugger                       PASS
Breakpoints                    PASS
Step / Continue                PASS
REPL                           PASS
REPL close / reopen            PASS
Clean shutdown                 PASS
PyInstaller build              PASS
Packaged runtime               PASS
Student import policy          PASS
```

The student import-policy work is isolated on:

```text
student-import-policy
```

until final review and merge.

Do not revisit previously resolved Python 3.15 runtime provisioning, debugger, REPL, QThread or PyInstaller issues unless new reproducible evidence requires it.