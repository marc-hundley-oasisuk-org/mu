# Mu Education Fork - Project Status

## Purpose

This repository is a school-focused fork of Mu Editor. The objective is not to reproduce unrestricted upstream Mu behaviour. The objective is to provide a maintainable Python editor suitable for managed educational environments, with curriculum boundaries and examination controls enforced by the application and its packaged runtime.

The current Windows baseline targets Python 3.15.0 and Mu 1.3.0.

## Core design principles

- Student Python execution is restricted to the agreed curriculum import allow-list.
- The student import policy is mandatory in all supported build profiles.
- Run, Debug and REPL use Mu's managed per-user Python 3.15 runtime.
- The Windows application is packaged with PyInstaller as a one-directory distribution.
- The PyInstaller distribution includes an independent Python 3.15 base runtime used to create the managed runtime.
- Examination restrictions are fail-safe: the source defaults to Exam behaviour and a packaged Exam build cannot be changed to Teaching by setting an environment variable at runtime.
- Build profiles control editor assistance only. They do not disable the student import policy.

## Current build profiles

### Exam

Exam is the default and fail-safe profile.

- Student import policy: enabled and mandatory
- Check: disabled
- Tidy: disabled
- F2 Check shortcut: disabled
- F10 Tidy shortcut: disabled
- Autocomplete: disabled
- API call tips/signatures: disabled
- QScintilla API assistance: not attached
- Unclosed-string visual warning: suppressed
- Brace matching/unmatched-brace assistance: disabled
- Normal syntax colouring: retained
- Run: retained
- Debug: retained
- REPL: retained

### Teaching

Teaching must be explicitly selected at build time.

- Student import policy: enabled and mandatory
- Check: enabled
- Tidy: enabled
- F2 Check shortcut: enabled
- F10 Tidy shortcut: enabled
- Autocomplete: enabled
- API call tips/signatures: enabled
- Unclosed-string visual warning: enabled
- Brace matching: enabled
- Run: retained
- Debug: retained
- REPL: retained

## Build-profile security boundary

The build script passes `MU_BUILD_PROFILE` to `package/pyinstaller.spec` only during packaging. The specification generates a PyInstaller runtime hook which sets `sys._mu_build_profile` inside the frozen application.

`mu/config.py` reads `sys._mu_build_profile` and otherwise defaults to Exam.

Consequently:

- source execution defaults to Exam;
- an unexpected profile value falls back to Exam;
- setting `MU_BUILD_PROFILE=Teaching` while launching source Mu does not enable Teaching features;
- setting `MU_BUILD_PROFILE=Teaching` while launching an already-built Exam `mu.exe` does not change the packaged profile;
- setting `MU_BUILD_PROFILE=Exam` while launching an already-built Teaching `mu.exe` does not change the packaged profile.

Both packaged behaviours have been manually validated.

## Student import policy

The curriculum policy applies consistently across Run, Debug and REPL.

Permitted direct student imports currently include:

- `math`
- `random`
- `time`
- `turtle`

Examples of prohibited direct imports include:

- `os`
- `socket`
- `pathlib`
- `subprocess`

The policy also covers `from ... import ...` and explicit `__import__()` use while permitting legitimate transitive dependencies required internally by allowed modules.

The policy is defence in depth, not a complete Python security sandbox. Endpoint security, permissions, application control, endpoint protection and network controls remain required.

## Python 3.15 modernisation

The project has been modernised around Python 3.15.0.

Completed work includes:

- managed-runtime creation moved from third-party `virtualenv` to standard-library `venv`;
- Python 3.15 managed runtime successfully created from a clean state;
- `ensurepip` and pip bootstrap validated;
- Run validated against the managed Python 3.15 interpreter;
- Debugger launch, breakpoint, Step and Continue validated;
- Jupyter QtConsole 5.7.2 / IPython 9.17.1 REPL validated;
- REPL close/reopen and application shutdown tested;
- student policy provisioning integrated into managed-runtime creation.

## Frozen Windows runtime architecture

A PyInstaller `mu.exe` cannot be used as a general-purpose Python interpreter. The packaged application therefore includes an independent Python 3.15 base installation.

Validated architecture:

```text
dist/
  mu/
    mu.exe
    _internal/
      python-runtime/
        python.exe
        pythonw.exe
        python3.dll
        python315.dll
        DLLs/
        Lib/
        ...
      mu/
        student_policy.py
        mu_debug.py
        debugger/
        wheels/
```

The bundled base runtime creates the per-user managed runtime. Student code, the debugger and the REPL then run from the managed runtime rather than from `mu.exe`.

## Runtime payload optimisation

The full copied Python 3.15 installation measured approximately 185.05 MB. The `Doc/` directory accounted for approximately 78.73 MB and has been excluded after validation.

The resulting bundled runtime is approximately 106 MB.

Further aggressive trimming has deliberately been avoided to preserve the known-good runtime baseline.

## PyInstaller packaging

Authoritative packaging files:

```text
package/prepare-pyinstaller.ps1
package/pyinstaller.spec
package/PYINSTALLER_BUILD.md
```

PyInstaller produces:

```text
dist/mu/mu.exe
```

The complete `dist/mu` directory is the application payload. `mu.exe` must not be distributed independently.

Current engineering builds intentionally retain `console=True` to expose missing imports, subprocess failures, Qt errors and resource problems during validation.

## Windows MSI packaging

The complete validated `dist/mu` directory is the authoritative input to the MSI stage.

The validated packaging chain is:

```text
Mu source
  -> PyInstaller
  -> validated dist/mu
  -> Master Packager Dev
  -> Mu Editor MSI
```

Validated MSI work includes:

- Master Packager Dev 2.3.0 packaging;
- machine-wide installation;
- application icon embedded in `mu.exe`;
- Start Menu shortcut;
- standard-user launch;
- silent installation;
- silent uninstall;
- Start Menu cleanup on uninstall;
- Program Files payload cleanup on uninstall;
- per-user managed Python runtime intentionally retained;
- silent reinstall of the same MSI.

The known validated MSI recovery point from the earlier packaging work was commit `496fcdc` for the Start Menu shortcut configuration.

## Testing status

### Examination editor restrictions

Validated from source:

- Check absent and underlying action blocked
- Tidy absent and underlying action blocked
- F2/F10 routes unavailable
- autocomplete absent
- API signatures/call tips absent
- unclosed-string warning background suppressed
- brace assistance disabled
- syntax colouring retained
- Run, Debug and REPL retained

Focused editor tests reached 54 passing tests after the code-assistance changes.

### Wider regression suite

A full regression run during the Check/Tidy work reported:

```text
1151 passed
20 skipped
10 failed
```

The remaining failures were in previously existing modernisation/test-maintenance areas including Jupyter GUI expectations, deprecated resource APIs, student-policy environment expectations and virtual-environment test fixtures. No failure was identified as a regression caused by the Check/Tidy feature controls.

### Packaged build profiles

Validated:

- default packaged build produces Exam behaviour;
- explicit Exam build produces Exam behaviour;
- explicit Teaching build restores the teaching-assistance features;
- student import restrictions remain enforced in Teaching;
- runtime environment variables cannot switch an Exam package to Teaching;
- runtime environment variables cannot switch a Teaching package to Exam.

## Repository workflow

The project uses focused feature branches and commits known-good recovery points before packaging changes. Recent work separated:

1. examination Check/Tidy restrictions;
2. editor code-assistance restrictions;
3. Exam/Teaching build-profile automation.

This separation should be retained for future changes.

## Current direction

The application architecture is now centred on a school-suitable controlled distribution rather than feature parity with unrestricted upstream Mu.

Future changes should preserve these boundaries:

- curriculum import policy remains mandatory;
- Exam remains the safe default;
- Teaching assistance must require explicit administrator selection at build time;
- deployed users must not be able to switch build profiles;
- packaging must continue to consume the complete validated PyInstaller payload;
- security-sensitive changes require source and packaged validation.
