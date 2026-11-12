# Mu Editor Windows MSI Packaging

## Purpose

This directory contains the Windows MSI packaging configuration for the Oasis Community Learning fork of Mu Editor.

The current application release is Mu 1.3.0 and requires Python 3.15.0.

The Windows packaging process produces a machine-wide MSI suitable for controlled enterprise deployment and subsequent packaging as a Microsoft Intune Win32 application.

## Packaging Architecture

The packaging chain is:

Mu source
    |
    +-- PyInstaller
            |
            +-- dist\mu
                    |
                    +-- Master Packager Dev
                            |
                            +-- Mu Editor MSI

PyInstaller is responsible for producing the complete Windows application payload.

Master Packager Dev packages that complete payload into the MSI.

The MSI packaging process must not manually reconstruct, selectively copy, or otherwise reproduce individual components from the PyInstaller distribution.

The authoritative MSI source payload is the complete:

dist\mu

directory.

## Prerequisites

The documented packaging baseline is:

- Mu Editor 1.3.0 source
- Python development environment used by the Mu project
- PyInstaller configuration under package\
- Master Packager Dev 2.3.0
- Windows environment for building and validating the MSI

The PyInstaller application build must be successfully validated before beginning MSI packaging.

## Repository Structure

Relevant files and directories include:

package\
    pyinstaller.spec
    prepare-pyinstaller.ps1
    PYINSTALLER_BUILD.md
    icons\
        mu.ico
    windows\
        package.json
        README.md

dist\
    mu\

release\
    Mu Editor 1.3.0.msi

The dist\mu directory is generated content and represents the complete application payload consumed by Master Packager Dev.

The release directory contains generated installer artefacts and test logs. These generated files are not intended to be committed to Git.

## PyInstaller and MSI Relationship

The MSI does not replace the PyInstaller packaging stage.

PyInstaller produces the complete runnable Mu application distribution. Master Packager Dev then packages that known-good distribution for Windows installation.

The required sequence is therefore:

1. Build and validate Mu.
2. Generate the complete dist\mu payload using PyInstaller.
3. Validate the generated application.
4. Package the complete dist\mu payload using Master Packager Dev.
5. Validate the resulting MSI.

Do not package mu.exe independently.

Do not selectively reconstruct the contents of dist\mu for the MSI.

## Generating dist\mu

From the repository root:

    .\package\prepare-pyinstaller.ps1

Then:

    .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean .\package\pyinstaller.spec

The resulting complete application payload is:

    dist\mu

Refer to package\PYINSTALLER_BUILD.md for the authoritative PyInstaller build documentation.

## Windows Application Icon

The Windows application icon is stored at:

    package\icons\mu.ico

package\pyinstaller.spec supplies this icon to the generated executable.

The resulting:

    dist\mu\mu.exe

contains the Mu application icon.

Windows Explorer can cache executable icons. A stale generic icon displayed for an existing filename does not by itself demonstrate that the icon is missing from the executable.

The icon implementation was validated using a clean PyInstaller build and an alternate executable filename.

## Master Packager Dev

The validated MSI tooling is:

    Master Packager Dev 2.3.0

The MSI configuration is:

    package\windows\package.json

Build the MSI from the repository root using:

    mpdev build .\package\windows\package.json

## package.json

package\windows\package.json defines the MSI packaging configuration.

The installation location is:

    %ProgramFiles%\Oasis\Mu

which results in the application being installed beneath:

    C:\Program Files\Oasis\Mu

The complete source payload is:

    dist\mu

The installed application executable is therefore:

    C:\Program Files\Oasis\Mu\mu.exe

## Permanent UpgradeCode

The MSI family UpgradeCode is:

    {84B5999E-CBE3-44E3-812D-2002DE81AD2D}

This value identifies the MSI product family and must remain stable across routine future Mu versions.

Do not generate a new UpgradeCode for each application release.

Upgrade behaviour must be validated separately before production release.

## Start Menu Shortcut

The MSI creates a Start Menu shortcut named:

    Mu Editor

The shortcut is configured in package.json and targets the installed Mu executable through the MSI shortcut configuration.

The installed shortcut has been validated at:

    C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Mu Editor.lnk

The shortcut is MSI-managed and may appear as an MSI-advertised shortcut rather than exposing the Program Files executable directly when inspected through WScript.Shell.

The shortcut has been functionally validated.

It:

- displays the correct Mu application icon
- launches Mu successfully
- launches Mu in the interactive user context
- permits normal Run operation
- permits REPL operation

No desktop shortcut is currently created.

## MSI Output

The current generated installer is:

    release\Mu Editor 1.3.0.msi

Generated MSI files and installer logs should not be committed to Git.

## Silent Installation

Installation must be performed from an elevated Windows context because the MSI installs machine-wide content beneath Program Files.

Example:

    msiexec.exe /i "release\Mu Editor 1.3.0.msi" /qn /norestart

For validation, verbose MSI logging should also be enabled.

Example:

    msiexec.exe /i "release\Mu Editor 1.3.0.msi" /qn /norestart /L*v "release\install.log"

A successful installation returns exit code:

    0

## Silent Uninstall

First obtain the currently installed ProductCode rather than assuming that a ProductCode from an earlier MSI build remains valid.

Example PowerShell:

    $mu = Get-ItemProperty `
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" ,
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" `
        -ErrorAction SilentlyContinue |
        Where-Object DisplayName -eq "Mu Editor"

    $mu | Select-Object DisplayName, DisplayVersion, PSChildName

Then:

    $productCode = $mu.PSChildName

    $p = Start-Process msiexec.exe `
        -ArgumentList "/x $productCode /qn /norestart /L*v `"release\uninstall.log`"" `
        -Wait `
        -PassThru

    $p.ExitCode

The validated uninstall exit code is:

    0

## Elevation Requirement

MSI installation and removal must be performed from an appropriately elevated context.

During development an uninstall attempted from a non-elevated PowerShell session returned MSI error 1730:

    You must be an Administrator to remove this application.

This was an execution-context issue rather than evidence of an MSI packaging defect.

The installed Mu application itself is intended to run in the standard interactive user context.

## MSI Logging

Use verbose MSI logging for installation, uninstall, upgrade and troubleshooting operations.

The standard logging form is:

    /L*v "<log-path>"

Generated installer logs should remain outside source control.

If an MSI operation fails, preserve the log before modifying the package.

## Managed Python Runtime

The machine-wide Mu installation and the managed Python environment have deliberately separate ownership.

The MSI owns the application beneath:

    C:\Program Files\Oasis\Mu

Mu manages its per-user Python runtime beneath:

    %LOCALAPPDATA%\python\mu

The MSI must not remove that managed per-user runtime during normal uninstallation.

The validated uninstall behaviour is:

    ProgramFilesExe : False
    ProgramFilesDir : False
    StartMenuLink   : False
    ManagedRuntime  : True

This means:

- the MSI-owned application executable is removed
- the MSI-owned Program Files directory is removed
- the MSI-owned Start Menu shortcut is removed
- the per-user managed Python environment is retained

## Standard-User Application Validation

Following machine-wide MSI installation, Mu has been validated from the Start Menu in the normal interactive user context.

Validated operations include:

- application launch
- normal Run
- REPL operation

The complete application baseline additionally includes successful Debug, breakpoint, Step, Continue and clean shutdown testing.

## Student Import Policy

The Mu 1.3.0 application implements a student import policy across:

- Run
- Debug
- REPL

Validated directly allowed student imports include:

- math
- random
- time
- turtle

Validated blocked examples include:

- os
- socket
- pathlib
- subprocess

The MSI must package the complete already-validated application payload. Installer engineering must not independently reconstruct the student-policy components.

## Validated Local MSI Lifecycle

The current Mu 1.3.0 MSI has passed the local MSI lifecycle test.

Validated behaviour includes:

- MSI build
- silent machine-wide installation
- Start Menu shortcut creation
- correct shortcut icon
- launch from the Start Menu
- Run smoke test
- REPL smoke test
- elevated silent uninstall
- removal of the Program Files executable
- removal of the Program Files application directory
- removal of the Start Menu shortcut
- retention of the managed per-user Python runtime
- silent reinstall
- successful post-reinstall launch
- post-reinstall Run and REPL smoke testing

The validated Git recovery point for the shortcut-enabled installer configuration is:

    496fcdc

## Expected Uninstall Behaviour

After MSI uninstall:

    C:\Program Files\Oasis\Mu\mu.exe

must not exist.

The directory:

    C:\Program Files\Oasis\Mu

must not remain.

The Start Menu shortcut:

    C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Mu Editor.lnk

must not remain.

The user-managed runtime:

    %LOCALAPPDATA%\python\mu

is deliberately retained.

## Upgrade Strategy

The permanent UpgradeCode must remain unchanged for routine future releases.

Upgrade behaviour has not yet been deliberately validated.

A future controlled validation must prove that a later-version MSI correctly upgrades Mu 1.3.0 without:

- duplicate MSI registrations
- stale Program Files content
- loss of the per-user managed runtime

The upgraded application must remain operational following the upgrade.

Do not permanently alter the Mu release version merely to perform an experimental upgrade test without first defining how the temporary test artefact will be handled.

## Clean VM Validation

Local lifecycle validation does not replace clean-environment testing.

The development workstation already contains the managed per-user Python environment, so first-time managed runtime provisioning has not yet been independently proved by the MSI/application lifecycle on a completely clean Windows user profile.

Clean VM validation remains mandatory before release.

It must include:

- silent MSI installation
- confirmation that no unexpected reboot occurs
- complete Program Files payload
- correct Start Menu shortcut and icon
- standard-user application launch
- confirmation that no managed runtime existed beforehand
- managed Python 3.15.0 provisioning
- ensurepip
- baseline package provisioning
- student policy validation
- Run
- Debug
- breakpoint
- Step
- Continue
- REPL
- REPL close and reopen
- clean shutdown
- student-policy ALLOW tests
- student-policy BLOCK tests
- silent uninstall
- Start Menu shortcut removal
- Program Files removal
- managed per-user runtime retention
- silent reinstall

## Signing Considerations

The current MPDEV build reports warnings relating to unsigned binaries.

Do not remove required runtime or application files merely to eliminate packaging warnings.

Code-signing requirements should be assessed as part of production release preparation.

## Endpoint and AppLocker Considerations

The current execution chain includes:

    C:\Program Files\Oasis\Mu\mu.exe

which uses the bundled runtime beneath the installed application payload and subsequently the managed per-user Python environment beneath:

    %LOCALAPPDATA%\python\mu

This execution architecture must be explicitly validated against OCL endpoint and AppLocker controls before broad deployment.

Do not assume that permitting the Program Files application automatically permits execution of the managed interpreter beneath the user's profile.

## Intune

Intune packaging is intentionally a later stage.

The intended packaging chain is:

Mu source
    |
    +-- PyInstaller
            |
            +-- dist\mu
                    |
                    +-- Master Packager Dev
                            |
                            +-- Mu MSI
                                    |
                                    +-- Microsoft Win32 Content Prep Tool
                                            |
                                            +-- .intunewin
                                                    |
                                                    +-- Intune Win32 app

Do not start Intune packaging until:

- MSI lifecycle validation has passed
- clean VM validation has passed
- upgrade behaviour has been validated
- endpoint and AppLocker behaviour has been assessed

## Release Principle

A release MSI must always begin with the complete known-good PyInstaller distribution.

The boundary is deliberate:

    application engineering -> PyInstaller -> validated dist\mu
    installer engineering   -> complete dist\mu -> MSI

Do not bypass that boundary by rebuilding application content inside the MSI packaging process.
