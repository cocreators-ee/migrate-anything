import base64
import imp
import importlib
import inspect
import os
import pkgutil
import sys
from collections import OrderedDict
from io import open

from migrate_anything.log import logger
from migrate_anything.storage import Storage

PY3 = sys.version_info[0] >= 3


class _CONFIG:
    storage = None  # type: Storage


def configure(storage):
    """
    Configure migrate-anything
    :param Storage storage:
    """
    _CONFIG.storage = storage


def _encode_code(code):
    """
    Convert source code to encoded format
    :param str code:
    :return str:
    """
    if PY3:
        code = code.encode("utf-8")

    code = base64.b64encode(code)

    if PY3:
        code = code.decode("utf-8")

    return code


def _decode_code(encoded):
    """
    Convert encoded code to readable format
    :param str encoded:
    :return str:
    """
    return base64.b64decode(encoded)


def _encode_module(module):
    """
    Convert a Python module to encoded code
    :param types.Module module:
    :return str:
    """
    src = inspect.getsourcefile(module)
    with open(src) as file:
        return _encode_code(file.read())


def _decode_module(name, b64):
    """
    Convert encoded code to plain Python code
    :param str code:
    :return types.Module:
    """
    module = imp.new_module(name)
    exec (_decode_code(b64), module.__dict__)
    return module


def _load_package(package):
    """
    Load the migrations in the package
    :param str package: Package name
    :return dict:
    """
    logger.info("Loading migrations from {}".format(package))
    sys.path.append(os.getcwd())
    importlib.import_module(package)
    migrations = {}

    for _, name, _ in pkgutil.walk_packages(sys.modules[package].__path__):
        full_name = package + "." + name
        logger.info(" - {}".format(full_name))

        module = importlib.import_module(full_name)
        _check_module(module)
        migrations[name] = module

    return migrations


def _check_module(module):
    """
    Quickly validate that module seems like a valid migration
    :param types.Module module:
    """
    if not getattr(module, "up", None):
        raise Exception("Module {} does not define up()".format(module))
    if not getattr(module, "down", None):
        raise Exception("Module {} does not define down()".format(module))


def _check_config():
    """
    Check that the configuration is sufficient
    """
    errors = False
    if not _CONFIG.storage:
        logger.error(
            "No storage configured for migrate-anything. Did you run configure()?"
        )
        errors = True

    if errors:
        sys.exit(1)


def _undo_migrations(migrations):
    """
    Undo any migrations that are no longer active
    :param dict[str, str] migrations: Old migrations to undo
    """
    for name in migrations:
        logger.info("Undoing migration {}".format(name))
        code = migrations[name]
        module = _decode_module(name, code)
        module.down()
        _CONFIG.storage.remove_migration(name)


def _apply_migrations(migrations):
    """
    Apply new migrations
    :param dict[str,types.Module] migrations:
    """
    for name in migrations:
        logger.info("Applying migration {}".format(name))
        module = migrations[name]
        module.up()
        _CONFIG.storage.save_migration(name, _encode_module(module))


def run(package):
    """
    Run the complete process
    :param str package: Name of the package that defines the migrations
    """

    # Package should define config, load it first, then check
    migrations = _load_package(package)
    _check_config()

    # Calculate diffs
    applied = OrderedDict(_CONFIG.storage.list_migrations())
    applied_keys = set(applied.keys())
    current = set(migrations.keys())

    if current:
        logger.info("Found previously applied migrations:")
        for name in sorted(applied_keys):
            logger.info(" - {}".format(name))

    undo_migrations = applied_keys - current
    new_migrations = current - applied_keys

    _undo_migrations(
        OrderedDict(
            [
                (name, applied[name])
                for name in reversed(applied)
                if name in undo_migrations
            ]
        )
    )

    _apply_migrations(
        OrderedDict(
            [(name, migrations[name]) for name in migrations if name in new_migrations]
        )
    )
