"""
Student Python import policy.

Defines the modules that student-authored Python code is permitted to
import when running under Mu's managed Python environment.

This is a curriculum restriction and defence-in-depth control. It is not
intended to provide a Python security sandbox.
"""

ALLOWED_IMPORTS = frozenset(
    {
        "math",
        "random",
        "time",
        "turtle",
    }
)


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
