# Student Python Import Policy

## Purpose

Mu includes a student-facing Python import policy intended to limit learners to the Python library modules required for the computing curriculum.

The policy is designed as a curriculum restriction and defence-in-depth measure.

It is not a security sandbox and must not be treated as the primary security boundary for the Windows device.

## Curriculum allow-list

Student-authored Python code is currently permitted to import:

- `math`
- `random`
- `time`
- `turtle`

All other direct student imports are rejected by default.

Examples of imports that are blocked include:

- `os`
- `sys`
- `socket`
- `subprocess`
- `pathlib`
- `shutil`
- `ctypes`

The allow-list is defined in:

    mu/student_policy.py

## Enforcement model

The policy distinguishes between imports initiated directly by student code and imports required internally by Python, Mu, the debugger, Jupyter/IPython and permitted modules.

This distinction is necessary because allowed modules may themselves depend on modules that students are not permitted to import directly.

For example:

    student code
        |
        +-- import turtle           ALLOWED
                |
                +-- tkinter         INTERNAL - ALLOWED
                +-- pathlib         INTERNAL - ALLOWED
                +-- os              INTERNAL - ALLOWED
                +-- sys             INTERNAL - ALLOWED

while:

    student code
        |
        +-- import os               BLOCKED

This allows the curriculum-approved module to function normally without exposing the same dependency as a permitted direct student import.

## Supported import forms

The policy applies to normal imports:

    import os

and from-import syntax:

    from os import path

It also intercepts explicit dynamic imports using:

    __import__("socket")

Top-level module names are used when evaluating imports.

For example:

    os.path

is evaluated against:

    os

## Student execution detection

Student execution is identified using the globals associated with the import request.

Normal Run and Debug student code executes with:

    __name__ == "__main__"

and the student's Python file as:

    __file__

Mu's Jupyter REPL executes student-entered commands with:

    __name__ == "__main__"
    __file__ == None

Known infrastructure launchers such as:

    mu_debug.py
    ipykernel_launcher.py

are explicitly excluded from student-context classification.

Imports initiated by modules such as `turtle`, IPython, ipykernel and Python standard-library dependencies are therefore not treated as direct student imports.

## Environment activation

Enforcement is additionally controlled by:

    MU_STUDENT_IMPORT_POLICY=1

Both conditions must be satisfied:

    policy environment flag enabled
                AND
    import originates from student context
                |
                v
          enforce allow-list

If the environment variable is absent, the hook remains installed but does not restrict imports.

This ensures that Mu infrastructure operations remain unrestricted, including:

- managed virtual environment creation;
- `ensurepip`;
- pip operations;
- baseline package installation;
- baseline package validation;
- Jupyter kernel registration;
- Mu's own Python dependencies.

Mu enables the policy specifically for student:

- Run;
- Debug;
- REPL.

## Managed Python integration

The policy operates inside Mu's managed Python 3.15 environment.

During managed-environment validation or creation, Mu determines the interpreter's `purelib` directory and provisions:

    Lib/site-packages/mu_student_policy.py
    Lib/site-packages/sitecustomize.py

`sitecustomize.py` contains a minimal bootstrap that installs the import hook.

The authoritative policy implementation remains:

    mu/student_policy.py

Mu copies this implementation into the managed environment as:

    mu_student_policy.py

This avoids requiring the managed environment to import the Mu application package.

## PyInstaller integration

The PyInstaller build explicitly preserves:

    mu/student_policy.py

as a physical data file.

This is required because packaged Mu must be able to copy the policy implementation into the separately managed Python environment.

The resulting application contains the physical policy beneath:

    dist/mu/_internal/mu/student_policy.py

The packaged policy and the provisioned managed-runtime policy have been validated as content-equivalent.

Their raw SHA256 values may differ on Windows because text-mode provisioning can normalise line endings between LF and CRLF.

Normalised content has been confirmed identical between:

1. repository `mu/student_policy.py`;
2. packaged `dist/mu/_internal/mu/student_policy.py`;
3. managed `Lib/site-packages/mu_student_policy.py`.

## Run behaviour

Python Mode Run enables:

    MU_STUDENT_IMPORT_POLICY=1

for the managed child Python process.

Allowed curriculum imports execute normally.

A prohibited direct import raises:

    StudentImportPolicyError

Run uses Python interactive mode, so the policy remains effective at the Python prompt after the script has completed.

## Debug behaviour

Debug enables:

    MU_STUDENT_IMPORT_POLICY=1

for the managed debugger process.

The debugger infrastructure itself remains trusted, while the student script is subject to the import policy.

Validation has confirmed that normal debugger functionality continues to operate, including:

- debugger startup;
- breakpoints;
- Step;
- Continue;
- permitted curriculum imports;
- rejection of prohibited student imports.

## REPL behaviour

The Jupyter/IPython kernel is launched using Mu's managed Python environment with:

    MU_STUDENT_IMPORT_POLICY=1

Kernel and IPython infrastructure imports remain unrestricted.

Commands entered by the learner are classified as student execution and are therefore subject to the allow-list.

REPL validation includes:

- permitted imports;
- blocked imports;
- expression execution;
- REPL close;
- REPL reopen;
- clean application shutdown.

## Student error

When a student attempts to import a module that is not permitted, Mu's managed Python environment raises:

    StudentImportPolicyError

The message identifies the prohibited module and lists the currently permitted modules.

For example:

    Module 'os' is not available in the student Python environment.
    Allowed modules: math, random, time, turtle

## Automated tests

Automated tests are located in:

    tests/test_student_policy.py

The focused policy suite contains 38 tests.

The tests cover:

- permitted module classification;
- prohibited module classification;
- top-level module handling;
- policy enable/disable values;
- Run context detection;
- REPL context detection;
- trusted infrastructure contexts;
- dependency contexts;
- hook installation;
- hook removal;
- disabled-policy behaviour;
- permitted dynamic imports;
- prohibited dynamic imports;
- normal import statements;
- from-import statements;
- permitted `turtle` dependencies.

The focused suite passes:

    38 passed

A full Mu test run during development produced:

    1151 passed
    20 skipped
    7 failed

The seven failures were outside the student-policy test suite and related to existing test expectations in the Python 3.15-modernised codebase.

They were not changed as part of the student import-policy implementation.

## Security limitations

The student import policy must not be described as a Python security sandbox.

The control reduces the Python modules directly available to learners and prevents straightforward access through prohibited imports.

It does not prove that arbitrary Python code is unable to reach equivalent functionality indirectly.

Examples of areas outside the guarantee of this policy include:

- objects already present in the interpreter;
- capabilities exposed through permitted modules;
- Python introspection;
- language-level functionality that does not require an import;
- filesystem operations explicitly available through Python builtins;
- operating-system security outside the Python interpreter.

Endpoint security must therefore remain enforced by the Windows device configuration, user permissions, application controls, endpoint protection and network controls.

## Maintenance

When changing the allow-list:

1. Update `ALLOWED_IMPORTS` in `mu/student_policy.py`.
2. Update the policy tests.
3. Run the focused test suite.
4. Validate Run.
5. Validate Debug.
6. Validate REPL.
7. Build the PyInstaller application.
8. Repeat the Run / Debug / REPL validation against packaged Mu.
9. Confirm the managed runtime received the updated policy.

Do not configure Mu mode dependencies, autocomplete API definitions or `mode_packages` as if they were import-security mechanisms. These systems serve different purposes.

## Current status

Version 1 of the student import allow-list is functionally complete.

Validated from source and packaged Mu:

    Run       PASS
    Debug     PASS
    REPL      PASS

Allowed:

    math
    random
    time
    turtle

Direct student access to modules outside the allow-list is rejected.