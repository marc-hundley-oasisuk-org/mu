"""
Tests for the student Python import policy.
"""

import builtins

import pytest

from mu import student_policy


@pytest.fixture(autouse=True)
def reset_import_hook(monkeypatch):
    """
    Restore the original import implementation and clear policy state around
    each test.
    """
    student_policy.remove_import_hook()
    monkeypatch.delenv(student_policy.POLICY_ENV_VAR, raising=False)

    yield

    student_policy.remove_import_hook()
    monkeypatch.delenv(student_policy.POLICY_ENV_VAR, raising=False)


@pytest.mark.parametrize(
    "module_name",
    [
        "math",
        "random",
        "time",
        "turtle",
        "turtle.example",
    ],
)
def test_allowed_imports(module_name):
    assert student_policy.is_import_allowed(module_name)


@pytest.mark.parametrize(
    "module_name",
    [
        "os",
        "os.path",
        "pathlib",
        "socket",
        "subprocess",
        "sys",
    ],
)
def test_disallowed_imports(module_name):
    assert not student_policy.is_import_allowed(module_name)


def test_validate_import_returns_allowed_name():
    assert student_policy.validate_import("math") == "math"


def test_validate_import_rejects_disallowed_name():
    with pytest.raises(
        student_policy.StudentImportPolicyError,
        match="Module 'socket' is not available",
    ):
        student_policy.validate_import("socket")


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
        "on",
        "ON",
    ],
)
def test_policy_enabled_values(value):
    assert student_policy.is_policy_enabled(
        {student_policy.POLICY_ENV_VAR: value}
    )


@pytest.mark.parametrize(
    "environment",
    [
        {},
        {student_policy.POLICY_ENV_VAR: ""},
        {student_policy.POLICY_ENV_VAR: "0"},
        {student_policy.POLICY_ENV_VAR: "false"},
        {student_policy.POLICY_ENV_VAR: "off"},
    ],
)
def test_policy_disabled_values(environment):
    assert not student_policy.is_policy_enabled(environment)


def test_run_context_is_student_context():
    context = {
        "__name__": "__main__",
        "__file__": r"C:\Users\Student\lesson.py",
    }

    assert student_policy.is_student_import_context(context)


def test_repl_context_is_student_context():
    context = {
        "__name__": "__main__",
        "__file__": None,
        "__package__": None,
    }

    assert student_policy.is_student_import_context(context)


@pytest.mark.parametrize(
    "filename",
    [
        r"C:\Mu\mu_debug.py",
        r"C:\Venv\site-packages\ipykernel_launcher.py",
    ],
)
def test_infrastructure_main_context_is_trusted(filename):
    context = {
        "__name__": "__main__",
        "__file__": filename,
    }

    assert not student_policy.is_student_import_context(context)


def test_dependency_context_is_not_student_context():
    context = {
        "__name__": "turtle",
        "__file__": r"C:\Python\Lib\turtle.py",
    }

    assert not student_policy.is_student_import_context(context)


def test_hook_is_installed_once():
    student_policy.install_import_hook()
    first_hook = builtins.__import__

    student_policy.install_import_hook()

    assert builtins.__import__ is first_hook
    assert builtins.__import__ is student_policy.student_import


def test_remove_hook_restores_original_import():
    student_policy.install_import_hook()
    student_policy.remove_import_hook()

    assert builtins.__import__ is student_policy._ORIGINAL_IMPORT


def student_globals():
    """Return globals matching a student script executed by Mu."""
    return {
        "__name__": "__main__",
        "__file__": r"C:\Users\Student\lesson.py",
        "__package__": None,
    }


def test_policy_disabled_allows_disallowed_import(monkeypatch):
    monkeypatch.delenv(student_policy.POLICY_ENV_VAR, raising=False)
    student_policy.install_import_hook()

    namespace = student_globals()
    exec("import socket", namespace)

    assert namespace["socket"].__name__ == "socket"


def test_policy_enabled_allows_permitted_dynamic_import(monkeypatch):
    monkeypatch.setenv(student_policy.POLICY_ENV_VAR, "1")
    student_policy.install_import_hook()

    namespace = student_globals()
    exec("module = __import__('math')", namespace)

    assert namespace["module"].__name__ == "math"



def test_policy_enabled_blocks_import_statement(monkeypatch):
    monkeypatch.setenv(student_policy.POLICY_ENV_VAR, "1")
    student_policy.install_import_hook()

    with pytest.raises(
        student_policy.StudentImportPolicyError,
        match="Module 'os' is not available",
    ):
        exec("import os", student_globals())


def test_policy_enabled_blocks_from_import(monkeypatch):
    monkeypatch.setenv(student_policy.POLICY_ENV_VAR, "1")
    student_policy.install_import_hook()

    with pytest.raises(
        student_policy.StudentImportPolicyError,
        match="Module 'os' is not available",
    ):
        exec("from os import path", student_globals())


def test_policy_enabled_blocks_dynamic_import(monkeypatch):
    monkeypatch.setenv(student_policy.POLICY_ENV_VAR, "1")
    student_policy.install_import_hook()

    namespace = student_globals()

    with pytest.raises(
        student_policy.StudentImportPolicyError,
        match="Module 'socket' is not available",
    ):
        exec("__import__('socket')", namespace)


def test_policy_enabled_allows_turtle_dependencies(monkeypatch):
    monkeypatch.setenv(student_policy.POLICY_ENV_VAR, "1")
    student_policy.install_import_hook()

    imported_module = __import__("turtle")

    assert imported_module.__name__ == "turtle"