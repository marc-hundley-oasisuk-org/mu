# Mu Windows PyInstaller Build

## Purpose

This document describes the maintained Windows packaging process for the Python 3.15 Mu fork.

The legacy packaging instructions referenced a `pyinstaller.spec` which was no longer present. The maintained packaging implementation is now:

```text
package\prepare-pyinstaller.ps1
package\pyinstaller.spec
package\PYINSTALLER_BUILD.rst
```

The objective is a reproducible distributable Windows build of Mu using Python 3.15.

## Current status

PyInstaller has successfully produced a Windows one-directory build of Mu under Python 3.15.

These packaging stages have previously completed successfully:

```text
Analysis
PYZ
PKG
EXE
COLLECT
```

The resulting executable is:

```text
dist\mu\mu.exe
```

Application launch, the Qt interface, editor operations, file operations and Python execution have previously been successfully tested from the packaged application.

The source application has subsequently received additional Python 3.15 runtime provisioning changes. A final packaged validation must therefore be completed after all source-level Python 3.15 functionality passes.

## Prerequisites

The current Windows development baseline uses:

- Windows 11
- Python 3.15.0
- Git
- PowerShell
- Repository-local `.venv`
- PyInstaller installed by the preparation process

The repository should be cloned locally rather than copying an existing development environment.

Generated environments and build directories should not be transferred between machines.

## Build configuration

The authoritative PyInstaller specification is:

```text
package\pyinstaller.spec
```

The specification must remain tracked in Git.

The generated directories must not be treated as source artefacts:

```text
build\
dist\
```

## Preparation

Open PowerShell in the repository root.

If required for the current PowerShell process:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

Run the preparation script:

```powershell
.\package\prepare-pyinstaller.ps1
```

Before packaging, confirm that Mu starts correctly from source:

```powershell
.\.venv\Scripts\python.exe .\run.py
```

Do not proceed to packaging when the source application is known to be failing.

## Build

From the repository root run:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller `
    --noconfirm `
    --clean `
    .\package\pyinstaller.spec
```

A successful build should create:

```text
dist\mu\mu.exe
```

The complete `dist\mu` directory is the distributable application at this stage.

Do not copy only `mu.exe` out of the directory. A PyInstaller one-directory build contains supporting files required by the executable.

## Run the packaged application

Launch from PowerShell during validation:

```powershell
.\dist\mu\mu.exe
```

Keeping a console visible during engineering validation is useful because missing imports, subprocess failures, Qt errors and resource problems can be observed directly.

The specification can be changed to disable the console for a release build only after validation has completed.

## Why one-directory

The current build intentionally uses the PyInstaller one-directory model.

Mu uses components including Qt, Python runtime processes, Jupyter components, debugger processes, resources and runtime package provisioning.

The one-directory layout makes those components substantially easier to inspect during development and troubleshooting.

Do not move to a one-file build until the one-directory build has reached a stable validated state.

## Runtime provisioning

The packaged Mu application must not be validated solely by checking that the user interface launches.

Mu creates a separate per-user Python environment for executing user code.

For Python 3.15, runtime provisioning includes:

- creating the Mu-managed Python environment;
- bootstrapping a Python 3.15-compatible pip;
- ensuring the default `pip.exe` launcher exists;
- installing Mu baseline packages;
- installing the Python 3.15-compatible Pygame implementation;
- registering the required runtime components;
- configuring the Jupyter kernel used by applicable functionality.

The first clean launch of a packaged build must therefore be tested with no existing Mu runtime environment present.

## Validation checklist

Source validation should be completed before packaged validation.

The packaged application should then be tested as a clean standard user.

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

### Python runtime

- [ ] Mu creates the per-user Python 3.15 runtime
- [ ] Runtime interpreter reports Python 3.15
- [ ] Runtime pip is functional
- [ ] Baseline packages are installed
- [ ] Simple Python program executes
- [ ] `sys.executable` points to the intended Mu runtime

### REPL

- [ ] REPL starts
- [ ] Kernel is located
- [ ] Input executes
- [ ] Output is displayed
- [ ] REPL shuts down cleanly

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

## Known limitation

The Python 3.15 REPL remains under investigation at the current development checkpoint.

A distributable executable may be generated for engineering testing, but the packaged application should not be treated as fully validated until the REPL issue has been resolved and the complete packaged validation checklist passes.

## Clean rebuild

When repeating deployment validation, remove previous PyInstaller-generated output before rebuilding if required.

The `--clean` PyInstaller option should continue to be used to prevent stale analysis data from obscuring packaging changes.

## Repository policy

Track:

```text
package\pyinstaller.spec
package\prepare-pyinstaller.ps1
package\PYINSTALLER_BUILD.rst
```

Do not track generated content such as:

```text
.venv\
build\
dist\
__pycache__\
*.pyc
```

## Release principle

A successful PyInstaller `EXE` or `COLLECT` stage proves that packaging completed. It does not prove that the resulting Mu application is ready for deployment.

The Windows build should only be considered validated after both the source and packaged application validation matrices pass.
