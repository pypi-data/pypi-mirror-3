"""General tests for the `fix.fix` module."""

from types import ModuleType

import fix.fix


def test_exists():
    """`fix.fix` module exists"""
    assert isinstance(fix.fix, ModuleType)
