from os.path import join, dirname, sep, exists

import pytest

from migrate_anything import CSVStorage
from migrate_anything.migrator import _check_module, run
from migrate_anything.tests.common import (
    GOOD_CODE,
    WITHOUT_DOWN,
    WITHOUT_UP,
    clean_files,
    clean_filesystem,
)

try:
    from importlib import invalidate_caches, machinery, util
except ImportError:

    def invalidate_caches():
        pass


MIGRATION_CODE = """
from os import remove
from time import time

file = "test-file2.txt"


def up():
    with open(file, "w") as f:
        f.write(str(time()))


def down():
    with open(file) as f:
        old = float(f.read())
        diff = abs(time() - old)
        if diff > 0.5:
            raise Exception("Something is wrong")
    remove(file)
"""

HERE = dirname(__file__)
TEST_CSV = join(HERE, "migrator_test.csv")
MIGRATIONS_PKG = "migrate_anything.tests.migrations"
MIGRATIONS_PATH = MIGRATIONS_PKG.replace(".", sep)
NEW_MIGRATION = join(MIGRATIONS_PATH, "02-good-code.py")


def test_check_module():
    module_spec = machinery.ModuleSpec("test", None)
    module = util.module_from_spec(module_spec)
    exec(GOOD_CODE, module.__dict__)

    _check_module(module)

    module_spec = machinery.ModuleSpec("test2", None) 
    module = util.module_from_spec(module_spec)
    exec(WITHOUT_DOWN, module.__dict__)
    with pytest.raises(Exception):
        _check_module(module)

    module_spec = machinery.ModuleSpec("test3", None)
    module = util.module_from_spec(module_spec)
    exec(WITHOUT_UP, module.__dict__)
    with pytest.raises(Exception):
        _check_module(module)


@clean_files([TEST_CSV, "test-file.txt", "test-file2.txt", NEW_MIGRATION])
def test_run():
    storage = CSVStorage(TEST_CSV)

    assert len(storage.list_migrations()) == 0

    run(MIGRATIONS_PKG)
    first = storage.list_migrations()

    assert len(first) > 0
    assert exists("test-file.txt")

    with open(NEW_MIGRATION, "w") as f:
        f.write(MIGRATION_CODE)

    clean_filesystem()
    invalidate_caches()  # Reset import caches

    run(MIGRATIONS_PKG)
    second = storage.list_migrations()

    assert len(second) > len(first)
    assert exists("test-file2.txt")

    clean_filesystem([NEW_MIGRATION])
    invalidate_caches()  # Reset import caches

    run(MIGRATIONS_PKG)
    third = storage.list_migrations()

    assert third == first
    assert not exists("test-file2.txt")


@clean_files([TEST_CSV, "test-file.txt", "test-file2.txt", NEW_MIGRATION])
def test_run_with_revert_mode():
    storage = CSVStorage(TEST_CSV)

    assert len(storage.list_migrations()) == 0

    run(MIGRATIONS_PKG)
    first = storage.list_migrations()

    assert len(first) > 0
    assert exists("test-file.txt")

    with open(NEW_MIGRATION, "w") as f:
        f.write(MIGRATION_CODE)

    clean_filesystem()
    invalidate_caches()  # Reset import caches

    run(MIGRATIONS_PKG)
    second = storage.list_migrations()

    assert len(second) > len(first)
    assert exists("test-file2.txt")

    invalidate_caches()  # Reset import caches

    run(MIGRATIONS_PKG, revert=True)
    third = storage.list_migrations()

    assert third == first
    assert not exists("test-file2.txt")
