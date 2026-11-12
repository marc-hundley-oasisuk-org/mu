# Mu Windows PyInstaller Build

## Purpose

This document describes the maintained Windows packaging process for the Python 3.15 education-focused Mu fork.

The maintained packaging implementation is:

```text
package\prepare-pyinstaller.ps1
package\pyinstaller.spec
package\PYINSTALLER_BUILD.md
```

The objective is a reproducible, redistributable Windows build of Mu using Python 3.15 with mandatory curriculum import restrictions and an administrator-selected Exam or Teaching editor profile.

Python 3.15.0 is mandatory for the current project.

---

## Current status

PyInstaller successfully produces a Windows one-directory build of Mu under Python 3.15.

The resulting executable is:

```text
dist\mu\mu.exe
```

The current packaged application has been functionally validated for:

- application startup;
- Python 3.15 managed-runtime provisioning;
- `ensurepip` and pip bootstrap;
- normal Python execution;
- debugger launch and connection;
- debugger breakpoints;
- debugger Step and Continue;
- REPL startup;
- REPL execution;
- REPL close and reopen;
- clean application shutdown with an active REPL;
- student import-policy provisioning;
- student import-policy enforcement across Run, Debug and REPL;
- Exam build-profile behaviour;
- Teaching build-profile behaviour;
- packaged profile immutability against runtime `MU_BUILD_PROFILE` changes.

The Python 3.15, student import-policy and Exam/Teaching architecture is therefore the current known-good Windows packaging baseline.

---

## Development baseline

The current Windows development baseline uses:

```text
Python                     3.15.0
PyInstaller                 6.22.3
pyinstaller-hooks-contrib   2026.8
PyQt5                       5.15.11
ipykernel                   7.4.0
IPython                     9.17.1
Jupyter QtConsole           5.7.2
```

Development also requires:

- Windows;
- Git;
- PowerShell;
- a repository-local `.venv`.

The repository should be cloned locally rather than copying an existing development environment.

Generated environments and PyInstaller output should not be transferred between development machines.

---

## Build configuration

The authoritative PyInstaller specification is:

```text
package\pyinstaller.spec
```

The supported build entry point is:

```text
package\prepare-pyinstaller.ps1
```

Both must remain tracked in Git.

Build-profile behaviour is implemented across:

```text
mu\config.py
package\prepare-pyinstaller.ps1
package\pyinstaller.spec
```

`mu\config.py` defaults to Exam when no frozen build profile is present.

`package\prepare-pyinstaller.ps1` accepts only:

```text
Exam
Teaching
```

and defaults to Exam.

`package\pyinstaller.spec` freezes the selected profile into the application using a generated PyInstaller runtime hook.

The generated runtime hook belongs under:

```text
build\
```

and must not be committed to Git.

The student import policy is deliberately independent of this mechanism and remains mandatory in all supported builds.

Generated directories must not be treated as source artefacts:

```text
build\
dist\
```

---

## Preparation and build profiles

Open PowerShell in the repository root.

If required for the current PowerShell process:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

The Windows build supports two administrator-selected editor-assistance profiles:

```text
Exam
Teaching
```

The student import policy is mandatory in both profiles and is not controlled by profile selection.

### Exam build

Exam is the default and fail-safe profile:

```powershell
.\package\prepare-pyinstaller.ps1
```

It may also be selected explicitly:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Exam
```

Exam produces:

```text
Student Import Policy : Enabled (mandatory)
Check                 : Disabled
Tidy                  : Disabled
Code Assistance       : Disabled
```

### Teaching build

Teaching must be selected explicitly:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Teaching
```

Teaching produces:

```text
Student Import Policy : Enabled (mandatory)
Check                 : Enabled
Tidy                  : Enabled
Code Assistance       : Enabled
```

### Build behaviour

`prepare-pyinstaller.ps1` performs both environment preparation and the PyInstaller build.

The script:

- selects the requested build profile;
- reports the effective configuration;
- creates the repository-local `.venv` when required;
- updates pip, setuptools and wheel;
- installs Mu into the build environment in editable mode;
- ensures PyInstaller is installed;
- checks the exit code of each critical native command;
- invokes `package\pyinstaller.spec`;
- verifies that `dist\mu\mu.exe` was created;
- terminates with an error when a critical preparation or build command fails;
- removes the temporary `MU_BUILD_PROFILE` environment value when complete or when the build fails.

The selected profile is frozen into the packaged application through a PyInstaller runtime hook.

`MU_BUILD_PROFILE` is a build-process input and not a deployed application setting. Changing this environment variable when launching an already-built application does not change its packaged profile.

Before packaging, source behaviour should already have been validated.

Do not proceed with release packaging when the source application is known to be failing.

### Packaging metadata

The repository uses `README.md` as the project README.

`setup.py` must therefore use `README.md` for the package long description rather than the obsolete root `README.rst` reference.

The long-description content type is:

```text
text/markdown
```

---

## Build

The supported Windows build entry point is:

```powershell
.\package\prepare-pyinstaller.ps1
```

Do not normally invoke PyInstaller directly because the preparation script controls the build profile supplied to `package\pyinstaller.spec`.

Before rebuilding, check whether a previous packaged Mu or related Python process is still running:

```powershell
Get-Process mu, python, pythonw -ErrorAction SilentlyContinue |
    Select-Object Id, ProcessName, Path
```

Do not indiscriminately terminate unrelated Python processes.

A running process can keep files within `dist` locked and cause PyInstaller `COLLECT` to fail with an access-denied error.

The preparation script invokes PyInstaller using `--noconfirm` and `--clean`.

A successful build creates:

```text
dist\mu\mu.exe
```

The complete `dist\mu\` directory is the distributable application.

Do not copy only `mu.exe` out of this directory. The current PyInstaller build uses the one-directory model and requires the supporting files under `dist\mu`.

---

## Run the packaged application

Launch the packaged application from PowerShell during engineering validation:

```powershell
.\dist\mu\mu.exe
```

The PyInstaller specification currently intentionally uses:

```text
console=True
```

Keeping the console visible during engineering validation allows missing imports, subprocess failures, Qt errors and resource problems to be observed directly.

Console mode should not be disabled until release packaging is deliberately addressed.

---

## Why one-directory

The current build intentionally uses the PyInstaller one-directory model.

Mu uses components including:

- Qt;
- an independent Python 3.15 base runtime;
- a per-user managed Python runtime;
- Jupyter components;
- external debugger processes;
- runtime package provisioning;
- physical runtime resources;
- the student import-policy deployment artefact.

The one-directory layout makes these components easier to inspect and validate during development.

Do not move to a one-file build while the current packaging architecture is being validated and maintained.

---

## Packaged Python architecture

A frozen PyInstaller `mu.exe` cannot be treated as a general-purpose Python interpreter.

When Mu is running from source, `sys.executable` is a suitable base interpreter.

When Mu is frozen with PyInstaller, `sys.executable` refers to `mu.exe` and cannot be used to create Mu's managed Python environment.

The packaged application therefore includes an independent Python 3.15 base installation.

The resulting architecture is conceptually:

```text
dist\
  mu\
    mu.exe
    _internal\
      python-runtime\
        python.exe
        pythonw.exe
        python3.dll
        python315.dll
        DLLs\
        Lib\
        ...
      mu\
        student_policy.py
        wheels\
          1.2.2.zip
        mu_debug.py
        debugger\
          config.py
          runner.py
          utils.py
```

The exact contents of `python-runtime` may be reduced through controlled optimisation, but the runtime must retain all components required for managed-runtime creation and Mu functionality.

---

## Bundled Python 3.15 base runtime

The authoritative PyInstaller specification determines the development interpreter's base Python executable and includes its installation as a PyInstaller `Tree`.

PyInstaller places the runtime under:

```text
dist\mu\_internal\python-runtime\
```

The packaged base interpreter is:

```text
dist\mu\_internal\python-runtime\python.exe
```

It must independently report:

```text
Python 3.15.0
```

The bundled Python installation has been validated as a portable base for Mu runtime provisioning.

It supports:

- Python 3.15 execution;
- standard-library `venv`;
- `ensurepip`;
- pip bootstrap;
- creation of Mu's per-user managed runtime.

The current packaging architecture deliberately uses the proven Python installation as the optimisation baseline rather than switching to Python's embeddable distribution.

The `Doc\` directory has been excluded from the bundled runtime as a validated payload optimisation.

The resulting bundled Python runtime is approximately 106 MB.

Further aggressive runtime trimming is not currently required.

---

## Managed runtime provisioning

Mu creates a separate per-user Python environment for executing user code.

Runtime provisioning uses the Python standard-library `venv` module rather than third-party `virtualenv` creation.

Conceptually, environment creation is:

```text
python.exe -I -m venv <managed-runtime>
```

Mu centrally determines the appropriate base interpreter.

During source execution this is the development Python interpreter.

During frozen Windows execution this resolves to:

```text
<directory-containing-mu.exe>\
    _internal\
    python-runtime\
    python.exe
```

The selected interpreter is maintained by `VirtualEnvironment` as its base interpreter and is used when creating the managed environment.

This distinction is required because frozen `mu.exe` cannot act as the Python interpreter for `python -m venv`.

Do not revert managed-runtime creation to running `virtualenv` through `sys.executable`.

---

## Managed runtime validation

A packaged Mu application must not be validated solely by checking that its user interface launches.

The first clean launch should be tested without an existing Mu per-user runtime so that the packaged Python base is exercised.

Runtime provisioning includes:

- creating the Mu-managed Python 3.15 environment;
- running the standard-library `venv` process;
- bootstrapping pip;
- installing Mu baseline packages;
- installing required runtime packages;
- registering the Jupyter kernel used by the REPL;
- provisioning the student import policy;
- provisioning the student-policy `sitecustomize.py` bootstrap.

Following provisioning:

```python
import sys
print(sys.version)
print(sys.executable)
```

must show Python 3.15 and the Mu-managed per-user runtime rather than `mu.exe` or the development virtual environment.

---

## Jupyter and REPL packaging

The Python 3.15 REPL is supported by the current packaged application.

The managed-runtime Jupyter stack includes:

```text
ipykernel 7.4.0
IPython 9.17.1
Jupyter QtConsole 5.7.2
```

Mu's generated wheel archive contains the Python 3.15-compatible runtime dependencies required by the managed environment.

The generated archive is:

```text
mu\wheels\1.2.2.zip
```

and is not tracked by Git.

The packaged copy is expected under:

```text
dist\mu\_internal\mu\wheels\1.2.2.zip
```

### ipykernel registration

When running frozen, `sys.executable` is `mu.exe` and must not be used to execute `ipykernel`.

Kernel registration therefore uses the interpreter inside Mu's newly created per-user managed runtime.

This ensures `ipykernel` is executed using the environment into which it has been installed.

### Jupyter Client provisioner discovery

Jupyter Client dynamically discovers kernel provisioners using entry-point metadata.

The relevant provisioner entry point includes:

```text
local-provisioner = jupyter_client.provisioning:LocalProvisioner
```

The PyInstaller specification therefore explicitly collects the required `jupyter_client.provisioning` modules and includes `jupyter_client` distribution metadata.

The packaged distribution is expected to contain the corresponding Jupyter Client metadata under `_internal`.

This is required for packaged REPL operation.

---

## Debugger packaging

The Mu debugger is deliberately launched using Mu's managed Python interpreter and physical Python source files.

The packaged debugger therefore requires physical copies of:

```text
dist\mu\_internal\mu\mu_debug.py
dist\mu\_internal\mu\debugger\config.py
dist\mu\_internal\mu\debugger\runner.py
dist\mu\_internal\mu\debugger\utils.py
```

These files are explicitly included by the PyInstaller specification.

The external debugger dependency chain is:

```text
mu_debug.py
    -> mu.debugger.config
    -> mu.debugger.runner
         -> mu.debugger.utils
```

Do not add additional debugger modules solely on the assumption that the entire package must exist physically. Add further files only when runtime evidence establishes that they are required.

---

## Student import policy

Mu includes a curriculum-focused import allow-list for student Python execution.

The permitted direct student imports are:

```text
math
random
time
turtle
```

The policy applies consistently to:

- Run;
- Debug;
- REPL.

The policy is mandatory in both Exam and Teaching builds.

### Policy architecture

The authoritative implementation is:

```text
mu\student_policy.py
```

The PyInstaller distribution must retain this as a physical data file.

`package\pyinstaller.spec` therefore explicitly includes `mu\student_policy.py`.

Expected packaged location:

```text
dist\mu\_internal\mu\student_policy.py
```

During managed-environment creation or validation, Mu determines the managed interpreter's `purelib` location and provisions:

```text
Lib\site-packages\mu_student_policy.py
Lib\site-packages\sitecustomize.py
```

`sitecustomize.py` installs the import hook when the managed interpreter starts.

The hook exists independently from policy activation.

Enforcement occurs only when:

```text
MU_STUDENT_IMPORT_POLICY=1
```

The variable is applied specifically to student Run, Debug and REPL execution.

Runtime provisioning, `ensurepip`, pip operations, baseline package installation, baseline package validation and Jupyter kernel registration remain unrestricted.

### Student versus dependency imports

The policy distinguishes between imports initiated directly by student code and imports required internally by permitted modules or Mu infrastructure.

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

This distinction is required because permitted modules such as `turtle` have legitimate dependencies that are not themselves on the student allow-list.

### Supported restriction forms

The policy blocks prohibited modules through ordinary imports:

```python
import os
```

from-import syntax:

```python
from os import path
```

and explicit dynamic imports:

```python
__import__("socket")
```

### Packaged policy integrity

The following policy copies have been validated as content-equivalent:

```text
mu\student_policy.py
dist\mu\_internal\mu\student_policy.py
<managed purelib>\mu_student_policy.py
```

Raw file hashes may differ when Windows text-mode processing changes line-ending representation.

Normalised file content has been confirmed identical.

### Security scope

The import policy is a curriculum restriction and defence-in-depth control.

It is not a complete Python security sandbox.

Endpoint security must continue to rely on the Windows device configuration, user permissions, application controls, endpoint protection and network controls.

---

## Critical packaged assets

The current known-good distribution requires the following critical assets:

```text
dist\mu\mu.exe
dist\mu\_internal\python-runtime\python.exe
dist\mu\_internal\mu\wheels\1.2.2.zip
dist\mu\_internal\mu\student_policy.py
dist\mu\_internal\mu\mu_debug.py
dist\mu\_internal\mu\debugger\config.py
dist\mu\_internal\mu\debugger\runner.py
dist\mu\_internal\mu\debugger\utils.py
```

Their presence should be checked when packaging changes affect PyInstaller data collection or the runtime payload.

---

## Current packaged validation

The current Python 3.15 packaged architecture has passed the following functional validation.

### Build profiles

The packaged profile mechanism has been validated for both supported profiles.

#### Exam validation

- [x] Exam is the default when no profile argument is supplied
- [x] Check is unavailable
- [x] Tidy is unavailable
- [x] autocomplete and API call tips are unavailable
- [x] unclosed-string visual assistance is suppressed
- [x] brace-matching assistance is disabled
- [x] student import policy remains enforced
- [x] setting `MU_BUILD_PROFILE=Teaching` at runtime does not alter the packaged Exam profile

#### Teaching validation

- [x] Teaching requires explicit build-time selection
- [x] Check is restored
- [x] Tidy is restored
- [x] autocomplete and API call tips are restored
- [x] normal unclosed-string assistance is restored
- [x] brace matching is restored
- [x] student import policy remains enforced
- [x] setting `MU_BUILD_PROFILE=Exam` at runtime does not alter the packaged Teaching profile

### Application

- [x] Mu launches
- [x] Packaged runtime provisioning succeeds
- [x] No fatal startup traceback

### Python runtime

- [x] Fresh per-user Python environment is created
- [x] Runtime reports Python 3.15.0
- [x] `ensurepip` works
- [x] pip works
- [x] Baseline/runtime packages install
- [x] Student-policy runtime files are provisioned

### Run

- [x] Normal Python program executes successfully
- [x] `sys.executable` resolves to Mu's per-user runtime
- [x] `math` permitted
- [x] `random` permitted
- [x] `time` permitted
- [x] `turtle` permitted
- [x] Prohibited direct imports rejected
- [x] Policy remains active for the interactive Python prompt following Run

### Debugger

- [x] Debugger starts
- [x] Debugger connects
- [x] Breakpoint is reached
- [x] Step works
- [x] Continue works
- [x] Program output is correct
- [x] Allowed curriculum imports operate
- [x] Prohibited student imports are rejected
- [x] Debugger finishes normally

### REPL

- [x] REPL opens
- [x] Python expression execution works
- [x] `2+2` returns `4`
- [x] Python version reports 3.15.0
- [x] Allowed curriculum imports operate
- [x] Prohibited student imports are rejected
- [x] REPL closes
- [x] REPL reopens
- [x] Reopened REPL executes successfully

### Shutdown

Controlled follow-up tests have passed:

- [x] Exit with REPL already closed
- [x] Exit with REPL active

One earlier packaged test produced:

```text
QThread: Destroyed while thread is still running
```

when exiting with an active REPL.

The warning did not reproduce during subsequent controlled tests with either a closed or active REPL.

It is therefore currently recorded as an intermittent observation rather than a reproducible packaging or lifecycle defect.

Do not change the existing QThread lifecycle implementation without new reproducible evidence.

---

## Student import-policy validation matrix

For policy-related release testing, validate all three student execution paths.

| Module / behaviour | Run | Debug | REPL |
|---|---|---|---|
| `math` | PASS | PASS | PASS |
| `random` | PASS | PASS | PASS |
| `time` | PASS | PASS | PASS |
| `turtle` | PASS | PASS | PASS |
| `os` | BLOCK | BLOCK | BLOCK |
| `socket` | BLOCK | BLOCK | BLOCK |
| `pathlib` | BLOCK | BLOCK | BLOCK |
| `subprocess` | BLOCK | BLOCK | BLOCK |
| prohibited `from ... import ...` | BLOCK | BLOCK | BLOCK |
| prohibited `__import__()` | BLOCK | BLOCK | BLOCK |
| permitted transitive dependencies | PASS | PASS | PASS |

When maintaining the policy, test both source Mu and the packaged application.

---

## Full validation checklist

Source validation should be completed before packaged validation.

For release or deployment testing, the packaged application should also be tested as a clean standard user.

### Application

- [ ] Mu launches
- [ ] No fatal import errors occur
- [ ] Qt resources and icons load
- [ ] Required Mu modes are available

### Files and editor

- [ ] New file
- [ ] Open file
- [ ] Save
- [ ] Save As
- [ ] Reopen saved file
- [ ] Normal editor operations

### Exam profile

- [ ] Check unavailable
- [ ] Tidy unavailable
- [ ] F2/F10 routes unavailable
- [ ] autocomplete unavailable
- [ ] API call tips unavailable
- [ ] unclosed-string visual assistance suppressed
- [ ] brace-matching assistance disabled
- [ ] runtime `MU_BUILD_PROFILE=Teaching` does not alter the profile

### Teaching profile

- [ ] Check available
- [ ] Tidy available
- [ ] F2/F10 routes available
- [ ] autocomplete available
- [ ] API call tips available
- [ ] normal unclosed-string assistance restored
- [ ] brace matching restored
- [ ] runtime `MU_BUILD_PROFILE=Exam` does not alter the profile

### Python runtime

- [ ] Mu creates a fresh per-user Python 3.15 runtime
- [ ] Runtime interpreter reports Python 3.15.0
- [ ] `ensurepip` succeeds
- [ ] Runtime pip is functional
- [ ] Baseline packages install
- [ ] Student-policy runtime files are provisioned
- [ ] Simple Python program executes
- [ ] `sys.executable` points to the intended Mu runtime

### Student import policy

- [ ] `math` permitted in Run
- [ ] `random` permitted in Run
- [ ] `time` permitted in Run
- [ ] `turtle` permitted in Run
- [ ] `os` rejected in Run
- [ ] `socket` rejected in Run
- [ ] `pathlib` rejected in Run
- [ ] `subprocess` rejected in Run
- [ ] prohibited `from ... import ...` rejected
- [ ] prohibited `__import__()` rejected
- [ ] allowed module dependencies continue to operate
- [ ] equivalent behaviour confirmed in Debug
- [ ] equivalent behaviour confirmed in REPL

### REPL

- [ ] REPL starts
- [ ] `2+2` returns `4`
- [ ] Python version reports 3.15.0
- [ ] REPL closes
- [ ] REPL reopens
- [ ] Reopened REPL executes
- [ ] Active REPL does not prevent clean application exit

### Debugger

- [ ] Debugger starts
- [ ] Debugger connects
- [ ] Breakpoint is reached
- [ ] Step works
- [ ] Continue works
- [ ] Debugger terminates cleanly

### Deployment

- [ ] Application runs as a standard user
- [ ] Complete `dist\mu` directory works on a clean test device
- [ ] Endpoint protection behaviour is validated
- [ ] AppLocker behaviour is validated if applicable
- [ ] No development virtual environment is required on the target device

---

## Runtime payload optimisation

The bundled Python 3.15 installation is a known-good runtime provisioning baseline.

Payload optimisation must therefore proceed incrementally rather than replacing the runtime architecture.

The following optimisation has been completed:

```text
Doc\
```

excluded from the bundled Python runtime.

This reduced the bundled Python installation from approximately 185.05 MB to approximately 106.32 MB, for a saving of approximately 78.73 MB.

Further aggressive trimming has deliberately been stopped.

Although `Lib\test` remains comparatively large, removing further components from the known-good Python installation is not currently justified by a deployment requirement.

Do not initially remove or substantially reduce:

```text
Lib\
DLLs\
python315.dll
python3.dll
vcruntime140.dll
vcruntime140_1.dll
```

Do not switch to Python's embeddable distribution without separate controlled validation.

### Runtime optimisation validation matrix

After each individual payload reduction:

1. Perform a clean PyInstaller build.
2. Verify `dist\mu\mu.exe` exists.
3. Verify `dist\mu\_internal\python-runtime\python.exe --version` returns Python 3.15.0.
4. Remove or rename the existing per-user Mu runtime so the packaged application cannot reuse it.
5. Launch packaged Mu.
6. Verify fresh managed-runtime provisioning completes.
7. Verify normal Python execution.
8. Verify the student import policy is provisioned.
9. Verify allowed and blocked imports.
10. Verify Debugger launch, breakpoint, Step, Continue, policy enforcement and termination.
11. Verify REPL open, execution, permitted/prohibited imports, close and reopen.
12. Exit Mu with the REPL active.
13. Record any QThread warning. Do not change lifecycle code unless the behaviour becomes reproducible.

Only after this matrix passes should another Python-runtime component be considered for removal.

---

## Known non-blocking build warnings

PyInstaller may report:

```text
Failed to collect submodules for 'mu.interface'
```

because importing `mu.interface` raises:

```text
NameError: name '_' is not defined
```

The current packaged application has nevertheless passed Run, Debugger, REPL and student-policy validation.

Do not change application code solely to remove this warning without evidence of a corresponding functional failure.

PyInstaller may also emit Black grammar cache write warnings.

These have not prevented successful packaging.

Do not treat every entry in `warn-pyinstaller.txt` as evidence of a missing runtime dependency.

Warnings should be investigated when they correlate with reproducible application behaviour.

---

## Clean rebuild

The supported clean build remains the profile-aware preparation script:

```powershell
.\package\prepare-pyinstaller.ps1
```

or:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Teaching
```

Before rebuilding, ensure no previous packaged Mu process or associated managed Python process is keeping files in `dist` open.

Check:

```powershell
Get-Process mu, python, pythonw -ErrorAction SilentlyContinue |
    Select-Object Id, ProcessName, Path
```

Do not indiscriminately terminate unrelated Python processes.

The build continues to use PyInstaller's `--clean` option so stale analysis data does not obscure packaging changes.

---

## Repository policy

Track:

```text
package\pyinstaller.spec
package\prepare-pyinstaller.ps1
package\PYINSTALLER_BUILD.md
package\BUILD_AND_RELEASE.md
docs\PROJECT_STATUS.md
docs\EXAM_TEACHING_PROFILES.md
mu\student_policy.py
tests\test_student_policy.py
```

Do not track generated content such as:

```text
.venv\
build\
dist\
__pycache__\
*.pyc
debug.log
```

Generated Mu runtime wheel archives should not be committed unless repository policy is deliberately changed.

---

## Release principle

Successful PyInstaller `EXE` and `COLLECT` stages prove that packaging completed.

They do not independently prove that the resulting Mu application is ready for deployment.

The Windows build should only be considered validated after the applicable source and packaged application validation matrices pass.

Runtime payload optimisation and profile changes must preserve:

- Python 3.15 managed-runtime provisioning;
- Run;
- Debug;
- REPL;
- mandatory student import-policy behaviour;
- packaged profile immutability;
- clean shutdown.

The current one-directory Python 3.15 architecture with the curriculum import allow-list and Exam/Teaching profile mechanism is the known-good baseline.
