import os
from subprocess import check_call, check_output

import pytest
from packaging import version


def removeprefix(str, prefix):
    return str[len(prefix) :] if str.startswith(prefix) else str


def assert_git_version(minimum_version):
    git_version = version.parse(
        removeprefix(
            check_output(["git", "--version"], encoding="ascii"), "git version "
        )
    )
    if git_version < version.parse(minimum_version):
        raise AssertionError(f"Tests require git >= {minimum_version}")


@pytest.fixture
def temp_working_dir(request, tmp_path):
    assert_git_version("2.28")  # Needed for `git branch -m` to succeed
    os.chdir(tmp_path)
    try:
        os.mkdir(".git")  # Tests write temp files here
        yield tmp_path
    finally:
        os.chdir(request.config.invocation_dir)


@pytest.fixture
def temp_git_repo(temp_working_dir):
    assert_git_version("2.28")  # Needed for `git branch -m` to succeed
    check_call(["git", "init", "--quiet"])
    check_call(["git", "branch", "-m", "main"])
    check_call(["git", "config", "user.email", "unit-test-runner@example.com"])
    check_call(["git", "config", "user.name", "Unit Test Runner"])
    yield temp_working_dir
