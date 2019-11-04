import csv
import sys
import types
from collections import namedtuple
from io import open

from migrate_anything.log import logger

try:
    from itertools import imap
except ImportError:
    imap = map

try:
    import pymongo
except ImportError:
    pymongo = None

try:
    import arango
    import arango.collection
except ImportError:
    arango = None

PY3 = sys.version_info.major >= 3

_CSVRow = namedtuple("Row", "name,code")


def _fix_docs(cls):
    """
    Used to copy function docstring from Storage baseclass to subclasses
    """
    for name, func in vars(cls).items():
        if isinstance(func, types.FunctionType) and not func.__doc__:
            for parent in cls.__bases__:
                parfunc = getattr(parent, name, None)
                if parfunc and getattr(parfunc, "__doc__", None):
                    func.__doc__ = parfunc.__doc__
                    break
    return cls


class Storage(object):
    def save_migration(self, name, code):
        """
        Save a migration
        :param str name: The name of the migration
        :param str code: The source code (encoded)
        """
        raise NotImplementedError("Storage class does not implement save_migration")

    def list_migrations(self):
        """
        List applied migrations
        :return List[Tuple[str, str]]:
        """
        raise NotImplementedError("Storage class does not implement list_migrations")

    def remove_migration(self, name):
        """
        Remove migration after it's been undone
        :param str name:
        """
        raise NotImplementedError("Storage class does not implement remove_migration")


@_fix_docs
class ArangoDBStorage(Storage):
    INDEX = ["name"]

    def __init__(self, collection, db=None, *args, **kwargs):
        """
        :param Union[arango.collection.Collection, str] collection: Either the
        Collection to store the migrations in, or the name of the collection.
        If the name is given, then the database must also be given.
        :param Optional[arango.database.Database] db: The arango database, only
        needed if the collection name is given rather than the collection.
        :param args: Positional arguments used if creating the collection
        :param kwargs: Keyword arguments used if creating the collection
        """
        if not arango:
            raise Exception("Cannot load arango, is it installed?")

        if not isinstance(collection, arango.collection.Collection):
            collection = self._get_collection(collection, db, *args, **kwargs)

        self.collection = collection

    @classmethod
    def _get_collection(cls, name, db, *args, **kwargs):
        """
        Get the collection for storing migrations. Creates it if needed.

        :param arango.database.Database db: The database
        :param str name: The name of the collection
        :param args: Positional arguments used if creating the collection
        :param kwargs: Keyword arguments used if creating the collection
        :return arango.collection.Collection: The collection
        """
        if not db:
            raise RuntimeError("Can not create collection without db.")

        if not db.has_collection(name):
            collection = db.create_collection(name,
                                              *args, **kwargs)
            collection.add_hash_index(cls.INDEX, unique=True)
        else:
            collection = db.collection(name)

        return collection

    def save_migration(self, name, code):
        self.collection.insert({"name": name, "code": code})

    def list_migrations(self):
        return [(e["name"], e["code"]) for e in self.collection.all()]

    def remove_migration(self, name):
        self.collection.delete_match({"name": name}, limit=1)


@_fix_docs
class CSVStorage(Storage):
    def __init__(self, file):
        self.file = file
        logger.warning(
            "Using CSV storage - hopefully you're just testing "
            "or know what you're doing as this data can be easily lost."
        )

    def save_migration(self, name, code):
        def _to_writable(value):
            return value if PY3 else value.encode("utf-8")

        mode = "a" if PY3 else "ab"
        with open(self.file, mode) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([_to_writable(name), _to_writable(code)])

    def list_migrations(self):
        migrations = []

        try:
            with open(self.file) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if not row:
                        continue
                    migrations.append(_CSVRow(*row))
        except IOError:
            pass

        return migrations

    def remove_migration(self, name):
        migrations = [
            migration for migration in self.list_migrations() if migration.name != name
        ]

        mode = "w" if PY3 else "wb"
        with open(self.file, mode) as csvfile:
            writer = csv.writer(csvfile)
            for row in migrations:
                writer.writerow(row)


@_fix_docs
class MongoDBStorage(Storage):
    INDEX = "name"

    def __init__(self, collection):
        """
        :param pymongo.collection.Collection collection:
        """
        if not pymongo:
            raise Exception("Cannot load pymongo, is it installed?")

        self.collection = collection

        if self.INDEX not in collection.index_information():
            collection.create_index(self.INDEX, unique=True)

    def save_migration(self, name, code):
        self.collection.insert_one({"name": name, "code": code})

    def list_migrations(self):
        return [(e["name"], e["code"]) for e in self.collection.find()]

    def remove_migration(self, name):
        self.collection.delete_one({"name": name})


__all__ = ["ArangoDBStorage", "CSVStorage", "MongoDBStorage"]
