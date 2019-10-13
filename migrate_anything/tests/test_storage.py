from collections import OrderedDict
from os.path import dirname, join

import pytest

from migrate_anything.migrator import _encode_code
from migrate_anything.storage import CSVStorage, Storage
from migrate_anything.tests.common import GOOD_CODE, clean_files

MIGRATIONS = OrderedDict([("01-test", _encode_code(GOOD_CODE))])

HERE = dirname(__file__)
TEST_CSV = join(HERE, "storage_test.csv")


def test_base_class():
    s = Storage()
    with pytest.raises(NotImplementedError):
        for name in MIGRATIONS:
            s.save_migration(name, MIGRATIONS[name])
            break

    with pytest.raises(NotImplementedError):
        s.list_migrations()

    with pytest.raises(NotImplementedError):
        for name in MIGRATIONS:
            s.remove_migration(name)
            break


@clean_files([TEST_CSV])
def test_csv_storage():
    s = CSVStorage(TEST_CSV)
    for name in MIGRATIONS:
        s.save_migration(name, MIGRATIONS[name])
        break

    received = s.list_migrations()
    assert len(s.list_migrations()) == len(MIGRATIONS)
    for name, code in received:
        assert name in MIGRATIONS
        assert code == MIGRATIONS[name]

    for name in MIGRATIONS:
        s.remove_migration(name)

    assert len(s.list_migrations()) == 0
