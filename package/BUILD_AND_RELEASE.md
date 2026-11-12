# Mu Education Fork - Build and Release Guide

## Supported baseline

Current validated Windows baseline:

```text
Mu Editor                  1.3.0
Python                     3.15.0
PyInstaller                 6.22.3
pyinstaller-hooks-contrib   2026.8
PyQt5                       5.15.11
ipykernel                   7.4.0
IPython                     9.17.1
Jupyter QtConsole           5.7.2
Master Packager Dev         2.3.0
```

## Repository components

Key application/security files:

```text
mu/config.py
mu/student_policy.py
mu/virtual_environment.py
mu/interface/editor.py
mu/interface/main.py
mu/logic.py
```

Key build files:

```text
package/prepare-pyinstaller.ps1
package/pyinstaller.spec
package/PYINSTALLER_BUILD.md
package/windows/package.json
package/windows/README.md
```

Key tests include:

```text
tests/test_student_policy.py
tests/test_logic.py
tests/interface/test_editor.py
tests/interface/test_main.py
```

## Build profiles

Exam is the default and should be used for assessment deployment.

```powershell
.\package\prepare-pyinstaller.ps1
```

or explicitly:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Exam
```

Teaching must be requested explicitly:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Teaching
```

The student import policy remains enabled in both profiles.

## Preparation and build behaviour

`prepare-pyinstaller.ps1`:

1. changes to the repository root;
2. selects the requested build profile;
3. reports the effective configuration;
4. creates `.venv` when required;
5. upgrades pip, setuptools and wheel;
6. installs Mu into the development environment in editable mode;
7. ensures PyInstaller is installed;
8. invokes PyInstaller with `package/pyinstaller.spec`;
9. verifies `dist/mu/mu.exe` exists;
10. removes the temporary build-profile environment value in a `finally` block.

## Profile banner

An Exam build should report values equivalent to:

```text
Mu Build Configuration
------------------------------------------------------------
Profile               : Exam
Student Import Policy : Enabled (mandatory)
Check                  : Disabled
Tidy                   : Disabled
Code Assistance        : Disabled
------------------------------------------------------------
```

A Teaching build should report:

```text
Profile               : Teaching
Student Import Policy : Enabled (mandatory)
Check                  : Enabled
Tidy                   : Enabled
Code Assistance        : Enabled
```

## PyInstaller profile freezing

`package/pyinstaller.spec` receives the profile from the build process and generates a runtime hook under generated `build/` content.

The runtime hook assigns the selected value to:

```python
sys._mu_build_profile
```

`mu/config.py` consumes this internal value. The environment variable itself is not used by the deployed application to select a profile.

## PyInstaller output

Successful packaging creates:

```text
dist/mu/mu.exe
```

The entire `dist/mu` directory must be treated as the distributable payload.

Do not copy `mu.exe` alone.

## Bundled Python runtime

The packaged distribution includes the development interpreter's validated Python 3.15 base installation under:

```text
dist/mu/_internal/python-runtime/
```

Key files include:

```text
python.exe
pythonw.exe
python3.dll
python315.dll
DLLs/
Lib/
```

`Doc/` is excluded as a validated payload reduction.

The bundled interpreter must report Python 3.15.0:

```powershell
.\dist\mu\_internal\python-runtime\python.exe --version
```

## Managed runtime

The frozen application uses the bundled Python interpreter to create the per-user managed environment using standard-library `venv`.

The intended chain is:

```text
dist/mu/mu.exe
    -> _internal/python-runtime/python.exe
    -> python -I -m venv
    -> per-user Mu managed runtime
    -> student Run / Debug / REPL
```

Kernel registration uses the managed runtime's own interpreter so `ipykernel` executes in the environment where it is installed.

## Student policy packaging

`mu/student_policy.py` must remain a physical packaged asset. Managed-runtime provisioning copies the policy and its `sitecustomize.py` bootstrap into the managed environment.

The policy is activated for student execution paths and remains mandatory for both Exam and Teaching profiles.

## Packaged Exam validation

At minimum validate:

### Application

- [ ] `mu.exe` starts
- [ ] no fatal console traceback
- [ ] icons/resources load

### Exam restrictions

- [ ] Check absent
- [ ] Tidy absent
- [ ] F2/F10 unavailable
- [ ] autocomplete absent
- [ ] call tips absent
- [ ] unclosed-string warning styling absent
- [ ] brace assistance absent
- [ ] runtime environment cannot enable Teaching

### Runtime

- [ ] clean managed-runtime provisioning works
- [ ] managed Python reports 3.15.0
- [ ] `ensurepip` works
- [ ] pip works

### Student execution

- [ ] Run works
- [ ] Debug works
- [ ] breakpoint works
- [ ] Step works
- [ ] Continue works
- [ ] REPL opens
- [ ] `2+2` returns `4`
- [ ] REPL closes and reopens

### Policy

- [ ] `math` permitted
- [ ] `random` permitted
- [ ] `time` permitted
- [ ] `turtle` permitted
- [ ] `os` blocked
- [ ] `socket` blocked
- [ ] `pathlib` blocked
- [ ] `subprocess` blocked
- [ ] equivalent enforcement confirmed across Run, Debug and REPL

## Packaged Teaching validation

Validate the same runtime and policy matrix, plus:

- [ ] Check restored
- [ ] Tidy restored
- [ ] F2/F10 restored
- [ ] autocomplete restored
- [ ] call tips restored
- [ ] unclosed-string warning styling restored
- [ ] brace matching restored
- [ ] runtime environment cannot switch the package to Exam

## MSI hand-off

Only a validated PyInstaller payload may proceed to MSI packaging.

```text
application engineering
    -> PyInstaller
    -> validated dist/mu
    -> installer engineering
    -> Master Packager Dev
    -> MSI
```

Master Packager Dev must consume the complete `dist/mu` directory. The MSI project must not reconstruct the Python runtime or select individual PyInstaller files.

## MSI lifecycle baseline

Previously validated Windows lifecycle behaviour includes:

- silent install succeeds;
- Start Menu shortcut exists and launches Mu;
- executable icon is embedded;
- Run and REPL smoke tests pass;
- elevated silent uninstall succeeds;
- Program Files payload is removed;
- Start Menu shortcut is removed;
- per-user managed runtime is retained;
- silent reinstall succeeds.

The permanent MSI `UpgradeCode` established by the packaging work must be preserved across appropriate upgrades.

## Known test debt

A full test run during the examination-control work reported 1151 passed, 20 skipped and 10 failures. The failures were associated with pre-existing Python 3.15/modernisation test maintenance, including Jupyter GUI expectations, resource API test assumptions, student-policy environment expectations and virtual-environment fixtures.

Do not mask these failures by weakening the new Exam/Teaching tests. Address them separately when maintaining the broader automated test baseline.

## Release gates

Before release:

1. source tests for the changed area pass;
2. source application behaves correctly for the intended profile;
3. PyInstaller completes from a clean build;
4. the packaged build profile is validated;
5. runtime environment-variable bypass tests fail safely;
6. clean managed Python provisioning succeeds;
7. Run, Debug and REPL pass;
8. the mandatory student import policy passes its allow/block matrix;
9. the complete `dist/mu` payload is validated before MSI generation;
10. MSI installation/uninstallation is validated as a standard user where applicable;
11. clean-device/VM and endpoint controls are validated before production deployment.
