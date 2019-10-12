import imp
import pytest
from migrate_anything.migrator import _check_module

GOOD_CODE = """
from time import time

def up():
    print(time())

def down():
    print(time())
"""

WITHOUT_DOWN = """
from time import time

def up():
    print(time())
"""

WITHOUT_UP = """
from time import time

def down():
    print(time())
"""


def test_check_module():
    module = imp.new_module("test")
    exec (GOOD_CODE, module.__dict__)

    _check_module(module)

    module = imp.new_module("test2")
    exec (WITHOUT_DOWN, module.__dict__)
    with pytest.raises(Exception):
        _check_module(module)

    module = imp.new_module("test3")
    exec (WITHOUT_UP, module.__dict__)
    with pytest.raises(Exception):
        _check_module(module)
