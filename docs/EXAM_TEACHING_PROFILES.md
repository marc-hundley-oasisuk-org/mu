# Mu Education Build Profiles

## Purpose

Mu supports two administrator-selected editor profiles: `Exam` and `Teaching`.

Both profiles are school-controlled builds. Neither profile disables the mandatory student import policy.

## Profile matrix

| Capability | Exam | Teaching |
|---|---|---|
| Student import policy | Enabled, mandatory | Enabled, mandatory |
| Check | Disabled | Enabled |
| Tidy | Disabled | Enabled |
| F2 Check | Disabled | Enabled |
| F10 Tidy | Disabled | Enabled |
| Autocomplete | Disabled | Enabled |
| API call tips/signatures | Disabled | Enabled |
| Unclosed-string visual warning | Disabled | Enabled |
| Brace matching assistance | Disabled | Enabled |
| Normal syntax colouring | Enabled | Enabled |
| Run | Enabled | Enabled |
| Debug | Enabled | Enabled |
| REPL | Enabled | Enabled |

## Fail-safe behaviour

Exam is the default.

`mu/config.py` does not trust a runtime environment variable to select the profile. It reads the build profile frozen into the application through `sys._mu_build_profile` and otherwise falls back to Exam.

An unrecognised or absent build profile therefore results in:

```text
BUILD_PROFILE       = Exam
ENABLE_CHECK        = False
ENABLE_TIDY         = False
ENABLE_CODE_ASSIST  = False
```

## Build selection

Default Exam build:

```powershell
.\package\prepare-pyinstaller.ps1
```

Explicit Exam build:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Exam
```

Teaching build:

```powershell
.\package\prepare-pyinstaller.ps1 -BuildProfile Teaching
```

The preparation/build script accepts only `Exam` and `Teaching` through PowerShell `ValidateSet` validation.

## Build-time implementation

The build flow is:

```text
prepare-pyinstaller.ps1
        |
        +-- selects Exam or Teaching
        |
        +-- sets MU_BUILD_PROFILE for the build process
        |
        v
pyinstaller.spec
        |
        +-- validates/falls back to Exam
        |
        +-- generates build/mu_build_profile_hook.py
        |
        v
PyInstaller runtime hook
        |
        +-- sets sys._mu_build_profile
        |
        v
mu/config.py
        |
        +-- selects immutable packaged feature flags
```

`MU_BUILD_PROFILE` is removed from the PowerShell environment by the build script in a `finally` block when packaging completes or fails.

## Security boundary

`MU_BUILD_PROFILE` is a build-process input only. It is not an application runtime configuration mechanism.

The following was validated against the packaged output:

```powershell
$env:MU_BUILD_PROFILE = "Teaching"
.\dist\mu\mu.exe
```

An Exam package remained Exam.

The inverse was also validated:

```powershell
$env:MU_BUILD_PROFILE = "Exam"
.\dist\mu\mu.exe
```

A Teaching package remained Teaching.

## Exam behaviour

Exam mode deliberately removes editor features that can provide answers, hints or corrective assistance during an assessment.

### Check and Tidy

The toolbar actions are not created. Their shortcuts are not registered. The underlying `check_code()` and `tidy_code()` paths are independently guarded by the build policy.

This means the restriction is not merely cosmetic.

### Autocomplete and call tips

Exam mode:

- sets the QScintilla auto-completion threshold to disabled;
- selects `QsciScintilla.AcsNone`;
- does not populate a `QsciAPIs` object with mode API definitions.

### Unclosed strings

Mu's themes normally give the `UnclosedString` lexer style a special background and end-of-line fill. Exam mode neutralises this visual warning after the Python lexer is attached, while retaining ordinary syntax colouring.

### Brace assistance

Exam mode selects `QsciScintilla.NoBraceMatch` instead of Mu's normal `SloppyBraceMatch`, preventing matched/unmatched brace feedback from acting as examination assistance.

## Teaching behaviour

Teaching explicitly restores Mu's teaching assistance:

- Check and Tidy toolbar actions;
- F2 and F10 shortcuts;
- autocomplete;
- API call tips/signatures;
- unclosed-string warning styling;
- brace matching assistance.

The student import policy remains enforced.

## Validation checklist

### Exam

- [ ] Check absent
- [ ] Tidy absent
- [ ] F2 does not invoke Check
- [ ] F10 does not invoke Tidy
- [ ] `print(` does not show call-tip assistance
- [ ] `os.` does not show autocomplete
- [ ] an unclosed string does not receive the special warning background
- [ ] unmatched braces do not receive brace-matching assistance
- [ ] syntax colouring remains
- [ ] Run works
- [ ] Debug works
- [ ] REPL works
- [ ] permitted imports work
- [ ] prohibited direct imports remain blocked
- [ ] runtime `MU_BUILD_PROFILE=Teaching` cannot alter the package

### Teaching

- [ ] Check available
- [ ] Tidy available
- [ ] F2 works
- [ ] F10 works
- [ ] autocomplete available
- [ ] call tips available
- [ ] unclosed-string warning styling restored
- [ ] brace matching restored
- [ ] Run works
- [ ] Debug works
- [ ] REPL works
- [ ] permitted imports work
- [ ] prohibited direct imports remain blocked
- [ ] runtime `MU_BUILD_PROFILE=Exam` cannot alter the package

## Maintenance rule

Do not add the student import policy to the profile switch. It is a mandatory educational control in this fork and must remain independent of Exam/Teaching editor-assistance selection.
