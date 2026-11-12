"""
Student Python import policy.

Defines and enforces the modules that student-authored Python code is
permitted to import when running under Mu's managed Python environment.

This is a curriculum restriction and defence-in-depth control. It is not
intended to provide a Python security sandbox.
"""

import builtins
import os
import sys


ALLOWED_IMPORTS = frozenset(
    {
        "math",
        "random",
        "time",
        "turtle",
    }
)

POLICY_ENV_VAR = "MU_STUDENT_IMPORT_POLICY"

ENABLED_ENV_VALUES = frozenset(
    {
        "1",
        "true",
        "yes",
        "on",
    }
)

TRUSTED_MAIN_FILES = frozenset(
    {
        "ipykernel_launcher.py",
        "mu_debug.py",
    }
)

_ORIGINAL_IMPORT = builtins.__import__
_IMPORT_HOOK_INSTALLED = False


class StudentImportPolicyError(ImportError):
    """Raised when student code attempts to import a disallowed module."""


def top_level_module(name):
    """
    Return the top-level component of an import name.

    For example, "package.submodule" becomes "package".
    """
    return name.partition(".")[0]


def is_import_allowed(name):
    """Return True when the requested module is permitted for student use."""
    return top_level_module(name) in ALLOWED_IMPORTS


def validate_import(name):
    """
    Validate a student-requested import.

    Return the supplied name when permitted, otherwise raise
    StudentImportPolicyError.
    """
    if not is_import_allowed(name):
        allowed = ", ".join(sorted(ALLOWED_IMPORTS))
        raise StudentImportPolicyError(
            "Module {!r} is not available in the student Python "
            "environment. Allowed modules: {}".format(name, allowed)
        )

    return name


def filename_only(path):
    """Return a normalised lowercase filename from a path."""
    if not path:
        return None

    return path.replace("\\", "/").rsplit("/", 1)[-1].lower()


def is_student_import_context(globals_dict):
    """
    Return True if import globals identify student-authored execution.

    Normal Run and Debug identify student code as __main__ with the
    student's filename. Mu's Jupyter REPL identifies student-entered code
    as __main__ without a __file__ value.

    Known infrastructure launchers are explicitly excluded.
    """
    if not globals_dict:
        return False

    if globals_dict.get("__name__") != "__main__":
        return False

    caller_file = globals_dict.get("__file__")

    if caller_file is None:
        return True

    return filename_only(caller_file) not in TRUSTED_MAIN_FILES


def is_policy_enabled(environ=None):
    """
    Return True when student import enforcement is explicitly enabled.

    Mu enables this only for student Run, Debug and REPL processes. Runtime
    provisioning, package installation and interpreter validation remain
    unrestricted.
    """
    if environ is None:
        environ = os.environ

    value = environ.get(POLICY_ENV_VAR, "")
    return str(value).strip().lower() in ENABLED_ENV_VALUES


def import_caller_globals(globals_dict):
    """
    Return the globals associated with the import request.

    Normal import statements supply globals directly. An explicit call to
    __import__ may omit them, so use the immediate caller's frame as a
    fallback.
    """
    if globals_dict is not None:
        return globals_dict

    try:
        return sys._getframe(2).f_globals
    except (AttributeError, ValueError):
        return None


def student_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Apply the student import policy when the caller is student code.

    Imports initiated internally by allowed modules or Mu infrastructure
    continue through Python's original import implementation.
    """
    caller_globals = import_caller_globals(globals)

    if is_policy_enabled() and is_student_import_context(caller_globals):
        validate_import(name)

    return _ORIGINAL_IMPORT(name, globals, locals, fromlist, level)


def install_import_hook():
    """Install the student import hook once for the current interpreter."""
    global _IMPORT_HOOK_INSTALLED

    if not _IMPORT_HOOK_INSTALLED:
        builtins.__import__ = student_import
        _IMPORT_HOOK_INSTALLED = True


def remove_import_hook():
    """Restore Python's original import implementation."""
    global _IMPORT_HOOK_INSTALLED

    builtins.__import__ = _ORIGINAL_IMPORT
    _IMPORT_HOOK_INSTALLED = False