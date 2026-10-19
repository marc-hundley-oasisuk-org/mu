Mu PyInstaller build
====================

This is a new validation-first PyInstaller build, not the obsolete process
formerly described by package/README.rst.

Windows build steps
-------------------

Run from PowerShell in the repository root::

    Set-ExecutionPolicy -Scope Process Bypass
    .\package\prepare-pyinstaller.ps1
    .\.venv\Scripts\python.exe .\run.py
    .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean .\package\pyinstaller.spec
    .\dist\mu\mu.exe

The initial specification creates a one-directory build and leaves the console
visible. This makes missing imports, Qt plug-in errors and resource failures
observable. Once validation is complete, change ``console=True`` to
``console=False`` in pyinstaller.spec and rebuild.

Validation checklist
--------------------

* Mu launches without an import or Qt plug-in error.
* The editor can create, save, reopen and run a basic Python file.
* Each required Mu mode opens.
* REPL input and output work.
* Debugger start, step and stop work.
* Serial-device detection works, if required in the deployment.
* Icons, translations and other resources load.
* The application starts as a standard user on a clean target device.
* AppLocker and endpoint protection rules are tested against the complete
  ``dist\mu`` directory.

Do not switch to a one-file build until the one-directory build is stable.
Qt, Jupyter, debugger subprocesses and bundled wheels are easier to diagnose
and operate from an extracted application directory.