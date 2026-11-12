# Mu: Python 3.15 Education Fork

This repository is a maintained education-focused fork of Mu, a simple Python code editor designed for beginner programmers.

The fork has been modernised for Python 3.15 and Windows deployment and includes additional controls intended for managed school environments.

The objective is not to reproduce unrestricted upstream Mu behaviour. The project provides a maintainable educational Python environment with curriculum restrictions and administrator-controlled levels of editor assistance.

## Project status

The current Python 3.15 Windows architecture has been functionally validated.

Current status:

- Python 3.15.0 development environment: working
- Mu application launch from source: working
- Mu-managed Python 3.15 runtime provisioning: working
- `ensurepip` and runtime pip provisioning: working
- Editor operations: working
- File open/save operations: working
- Python execution: working
- Debugger launch and connection: working
- Breakpoints, Step and Continue: working
- REPL startup and execution: working
- REPL close and reopen: working
- Windows PyInstaller one-directory build: working
- Packaged Python 3.15 base runtime: working
- Clean managed-runtime provisioning from the packaged application: working
- Student import-policy provisioning: working
- Student import-policy enforcement across Run, Debug and REPL: working
- Exam editor restrictions: working
- Teaching editor assistance profile: working
- Build-time Exam/Teaching profile selection: working
- Packaged profile immutability: validated

## Educational security model

The student import policy is a mandatory control in this fork.

Permitted direct student imports currently include:

```text
math
random
time
turtle
```

Direct access to modules outside the curriculum allow-list is restricted across Run, Debug and REPL.

The project supports two editor-assistance profiles.

### Exam

Exam is the default and fail-safe build profile.

It disables:

- Check
- Tidy
- F2 and F10 routes to those features
- autocomplete
- API call tips and signatures
- unclosed-string visual assistance
- brace-matching assistance

Normal syntax colouring, Run, Debug and REPL remain available.

### Teaching

Teaching must be explicitly selected by a systems administrator at build time.

It restores:

- Check and Tidy
- their keyboard shortcuts
- autocomplete
- API call tips
- syntax-error visual assistance
- brace matching

The mandatory student import policy remains enforced in Teaching builds.

The selected profile is frozen into the packaged application. A deployed user cannot convert an Exam package into Teaching by setting `MU_BUILD_PROFILE`.

## Project documentation

The current project documentation is:

- `Modernisation_notes.md` - historical engineering and modernisation notes.
- `docs/PROJECT_STATUS.md` - current architecture, completed work and project status.
- `docs/student_import_policy.md` - curriculum import-policy design and implementation.
- `docs/EXAM_TEACHING_PROFILES.md` - Exam and Teaching profile design, controls and validation.
- `package/BUILD_AND_RELEASE.md` - end-to-end build, validation and release procedure.
- `package/PYINSTALLER_BUILD.md` - detailed Windows PyInstaller architecture and engineering guidance.

## Python 3.15 runtime

Mu uses two distinct Python environments:

1. The environment used to run the Mu application.
2. A Mu-managed per-user runtime used to execute user Python code.

On Windows, the managed runtime is created below the user's local application data directory.

The Python 3.15 modernisation work restores Mu's runtime provisioning process and addresses compatibility issues encountered when creating that environment.

Current changes include:

- runtime provisioning through `venv.ensure_and_create()`;
- Python 3.15 virtual environment creation;
- runtime pip bootstrapping using Python's bundled `ensurepip`;
- runtime pip upgrade to a Python 3.15-compatible version;
- creation of the default `pip.exe` launcher expected by Mu;
- use of `pygame-ce` for Python 3.15 Pygame compatibility;
- controlled Pygame Zero dependency handling to avoid attempting to build an incompatible upstream Pygame release from source.

## Development setup

The current supported development target is:

- Windows 11
- Python 3.15.0
- Git
- PowerShell
- a repository-local Python virtual environment

After cloning the repository, create and prepare the development virtual environment as required by the project.

Mu can then be launched from the repository root with:

```powershell
.\.venv\Scripts\python.exe .\run.py
```

Python 3.15 is an intentional requirement. Compatibility issues should be investigated rather than worked around by downgrading the runtime.

## Windows distributable build

Windows packaging is controlled through:

```text
package\prepare-pyinstaller.ps1
package\pyinstaller.spec
```

The build process supports two administrator-selected profiles.

### Exam build

Exam is the default:

```powershell
.\package\prepare-pyinstaller.ps1
```

It may also be selected explicitly:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Exam
```

### Teaching build

Teaching must be explicitly requested:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Teaching
```

The preparation script:

- selects and reports the requested profile;
- prepares the repository-local build environment;
- updates pip, setuptools and wheel;
- installs Mu into the build environment;
- ensures PyInstaller is available;
- invokes PyInstaller;
- verifies that the packaged executable was created;
- removes temporary build-profile environment state when complete or when the build fails.

A successful build produces:

```text
dist\mu\mu.exe
```

Mu uses the PyInstaller one-directory model. The complete `dist\mu\` directory is the distributable application and must be kept together.

The packaged application includes an independent Python 3.15 base runtime used to provision Mu's per-user managed Python environment.

The selected Exam or Teaching profile is frozen into the packaged application at build time. Runtime environment variables do not change the profile of an already-built application.

See:

```text
package\PYINSTALLER_BUILD.md
package\BUILD_AND_RELEASE.md
```

for the detailed Windows build, architecture and validation procedures.

## Validation approach

Changes to this fork follow a validation-first process:

1. Establish a clean baseline.
2. Reproduce and inspect the failure or requirement.
3. Identify the exact compatibility or control point.
4. Make one targeted change.
5. Validate the source application.
6. Commit the validated change.
7. Rebuild and validate the packaged application when the source baseline is stable.

This keeps the modernisation and education-control work auditable and minimises unrelated changes.

## Upstream Mu

Mu is a modal Python editor originally designed around feedback from teachers and learners, with modes supporting different Python environments and devices.

This repository retains the original Mu source, documentation, licence and attribution while providing the additional work required for this maintained education-focused fork.

- Original Mu website: https://codewith.mu/
- Original Mu developer documentation: https://mu.readthedocs.io/

## Licence and attribution

The original project's licence and contributor attribution are retained in:

- `LICENSE`
- `AUTHORS.rst`

Modernisation work in this fork does not replace the copyright, licence or attribution of the original Mu project.
