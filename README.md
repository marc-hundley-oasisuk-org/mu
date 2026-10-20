# Mu: Python 3.15 Modernisation Fork

This repository is a maintained fork of Mu, a simple Python code editor designed for beginner programmers.

The upstream Mu project is no longer maintained. This fork is being modernised for continued use, with the current development branch focused on Python 3.15 and Windows deployment.

**Current development branch:** `python315`

## Project status

The Python 3.15 work is under active development and validation. It should not yet be considered a production release.

Current validation status:

- Python 3.15.0 development environment: working
- Mu application launch from source: working
- Mu-managed Python 3.15 runtime provisioning: working
- Runtime pip provisioning: working
- Editor operations: working
- File open/save operations: working
- Python execution: working
- Debugger bootstrap: working
- Breakpoints/debugging: working
- REPL: known issue under investigation
- Windows PyInstaller build: working at the basic packaging level
- Packaged Python 3.15 runtime validation: requires completion after source validation is finished

The current engineering priority is to resolve the REPL issue and complete source-level Python 3.15 compatibility before final validation of the distributable Windows build.

## Python 3.15 runtime

Mu uses two distinct Python environments:

1. The environment used to run the Mu application.
2. A Mu-managed per-user runtime used to execute user Python code.

On Windows, the managed runtime is created below the user's local application data directory.

The Python 3.15 modernisation work restores Mu's runtime provisioning process and addresses compatibility issues encountered when creating that environment.

Current changes include:

- Runtime provisioning through `venv.ensure_and_create()`.
- Python 3.15 virtual environment creation.
- Runtime pip bootstrapping using Python's bundled `ensurepip`.
- Runtime pip upgrade to a Python 3.15-compatible version.
- Creation of the default `pip.exe` launcher expected by Mu.
- Use of `pygame-ce` for Python 3.15 Pygame compatibility.
- Controlled Pygame Zero dependency handling to avoid attempting to build an incompatible upstream Pygame release from source.

## Development setup

The current supported development target for this branch is:

- Windows 11
- Python 3.15.0
- Git
- PowerShell
- A repository-local Python virtual environment

After cloning the repository, create and prepare the development virtual environment as required by the project.

Mu can then be launched from the repository root with:

```powershell
.\.venv\Scripts\python.exe .\run.py
```

Python 3.15 is an intentional requirement for this branch. Compatibility issues should be investigated rather than worked around by downgrading the runtime.

## Windows distributable build

A maintained PyInstaller configuration is included for producing a distributable Windows build.

Relevant files:

```text
package\prepare-pyinstaller.ps1
package\pyinstaller.spec
package\PYINSTALLER_BUILD.rst
```

Basic build sequence from PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass

.\package\prepare-pyinstaller.ps1

.\.venv\Scripts\python.exe .\run.py

.\.venv\Scripts\python.exe -m PyInstaller `
    --noconfirm `
    --clean `
    .\package\pyinstaller.spec
```

The resulting application is created under:

```text
dist\mu\mu.exe
```

The current packaging model is a PyInstaller one-directory build. This is deliberate while Python 3.15 compatibility is still being validated because it makes application resources, Python components and subprocess behaviour easier to inspect.

See `package/PYINSTALLER_BUILD.rst` for the full Windows build and validation procedure.

A successful PyInstaller build does not by itself establish that Mu is ready for deployment. The packaged application's editor, managed runtime, REPL and debugger must also pass validation.

## Known issues

### REPL

The Python REPL is not yet considered working under the current Python 3.15 implementation.

REPL remediation should remain separate from the completed runtime provisioning work so that each compatibility change can be independently tested and reviewed.

### Packaging

PyInstaller has successfully produced a Windows executable under Python 3.15.

Final packaged validation will be repeated after the remaining source-level Python 3.15 issues are resolved.

## Validation approach

Changes to this fork follow a validation-first process:

1. Establish a clean baseline.
2. Reproduce and inspect the failure.
3. Identify the exact compatibility issue.
4. Make one targeted change.
5. Validate the source application.
6. Commit the validated change.
7. Rebuild the packaged application when the source baseline is stable.

This is intended to keep the modernisation work auditable and minimise unrelated changes.

## Repository documentation

- `Modernisation_notes.md`: current modernisation state and technical notes.
- `package/PYINSTALLER_BUILD.rst`: Windows PyInstaller build procedure.
- `docs/`: original Mu developer and architecture documentation.
- `CONTRIBUTING.rst`: contributor information.
- `CHANGES.rst`: upstream project change history.
- `ROADMAP.rst`: upstream roadmap information.

## Upstream Mu

Mu is a modal Python editor originally designed around feedback from teachers and learners, with modes supporting different Python environments and devices.

This repository retains the original Mu source, documentation, licence and attribution while providing the additional work required for this maintained fork.

- [Original Mu website](https://codewith.mu/)
- [Original Mu developer documentation](https://mu.readthedocs.io/)

## Licence and attribution

The original project's licence and contributor attribution are retained in:

- `LICENSE`
- `AUTHORS.rst`

Modernisation work in this fork does not replace the copyright, licence or attribution of the original Mu project.
