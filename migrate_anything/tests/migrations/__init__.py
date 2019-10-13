from migrate_anything import configure, CSVStorage
from migrate_anything.tests.test_migrator import TEST_CSV

configure(storage=CSVStorage(TEST_CSV))
