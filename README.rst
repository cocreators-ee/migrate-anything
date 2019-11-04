.. image:: https://travis-ci.org/lieturd/migrate-anything.svg?branch=master
    :target: https://travis-ci.org/lieturd/migrate-anything

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://codecov.io/gh/Lieturd/migrate-anything/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Lieturd/migrate-anything

.. image:: https://sonarcloud.io/api/project_badges/measure?project=Lieturd_migrate-anything&metric=alert_status
    :target: https://sonarcloud.io/dashboard?id=Lieturd_migrate-anything

.. image:: https://img.shields.io/github/issues/lieturd/migrate-anything
    :target: https://github.com/Lieturd/migrate-anything/issues
    :alt: GitHub issues

.. image:: https://img.shields.io/pypi/dm/migrate-anything
    :target: https://pypi.org/project/migrate-anything/
    :alt: PyPI - Downloads

.. image:: https://img.shields.io/pypi/v/migrate-anything
    :target: https://pypi.org/project/migrate-anything/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/migrate-anything
    :target: https://pypi.org/project/migrate-anything/
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause

Migrate anything - database (etc.) migration utility, especially for Python projects.


What is this?
=============

It's kinda annoying how often you run into the question of how to handle migrations in your project, and there hasn't seem to emerged any good, DB -agnostic, framework-agnostic, and storage-agnostic tool to manage them.

This project is an attempt to change that.

Basically what it does when you run :code:`migrate-anything migrations` is:

1. Find all the files :code:`migrations/*.py` and sort them
2. Any that are not yet registered in the DB will be loaded, their :code:`up()` is executed, and the file's contents stored in the DB
3. Any files that are missing from the fs but are in the DB will have their code loaded from the DB and their :code:`down()` is executed - in reverse order


License
-------

Licensing is important. This project uses BSD 3-clause license, and adds no other dependencies to your project (it does use a few things during build & testing) - that's about as simple, safe, and free to use as it gets.

For more information check the `LICENSE <https://github.com/Lieturd/migrate-anything/blob/master/LICENSE>`_ -file.


Usage examples
==============

Firstly you'll need this package in your project. Pick one of these:

.. code-block:: python

    pip install -U migrate-anything
    poetry add migrate-anything
    pipenv install migrate-anything

Simply put, create a Python package, don't be too clever and call it e.g. ``migrations``. Then put files in that package:

.. code-block:: python

    # migrations/__init__.py
    from migrate_anything import configure, CSVStorage

    configure(storage=CSVStorage("migration_status.csv"))

.. code-block:: python

    # migrations/01-initialize-db.py
    # Please note that this is built for a completely hypothetical DB layer
    from my_db import get_db

    DB = get_db()

    def up():
        DB.create_table("example")

    def down():
        DB.delete_table("example")

This would configure your migrations' status to be stored in a local file called ``migration_status.csv`` and set up your first migration script. If you have a ``my_db`` module that works like this you could just run this with a single command:

.. code-block:: shell

    migrate-anything migrations
    poetry run migrate-anything migrations
    pipenv run migrate-anything migrations

Now in the real world you might want something more durable and a realistic example, so here's e.g. what you'd do when using MongoDB:

.. code-block:: python

    # __init__.py
    from migrate_anything import configure, MongoDBStorage
    import pymongo

    db = pymongo.MongoClient().my_db

    configure(storage=MongoDBStorage(db.migrations))

.. code-block:: python

    # 01-initialize-db.py
    from pymongo import MongoClient

    client = MongoClient()
    db = client.my_db

    def up():
        db.posts.insert_one({
            "id": "post-1",
            "title": "We're live!",
            "content": "This is our first post, yay."
        })
        db.posts.create_index("id")

    def down():
        db.posts.drop()

This would configure storage to a ``my_db.migrations`` MongoDB collection.

Future ideas include support for other DB engines (feel free to contribute),
and Kubernetes ConfigMap. Annoyingly storage to Kubernetes from inside a pod
and in code is not quite as simple as just running ``kubectl``.

Oh and your Kubernetes pods will likely require the necessary RBAC rules to manage their ConfigMap. It's unfortunately kinda complex, but I'm sure you can figure it out e.g. with this `guide <https://docs.bitnami.com/kubernetes/how-to/configure-rbac-in-your-kubernetes-cluster/>`_.

Alternatively you can just write your own - it's easy.

.. code-block:: python

    # __init__.py
    from migrate_anything import configure


    class CustomStorage(object):
        def __init__(self, file):
            self.file = file

        def save_migration(self, name, code):
            with open(self.file, "a", encoding="utf-8") as file:
                file.write("{},{}\n".format(name, code))

        def list_migrations(self):
            try:
                with open(self.file, encoding="utf-8") as file:
                    return [
                        line.split(",")
                        for line in file.readlines()
                        if line.strip()  # Skip empty lines
                    ]
            except FileNotFoundError:
                return []

        def remove_migration(self, name):
            migrations = [
                migration for migration in self.list_migrations() if migration[0] != name
            ]

            with open(self.file, "w", encoding="utf-8") as file:
                for row in migrations:
                    file.write("{},{}\n".format(*row))


    configure(storage=CustomStorage("test.txt"))

You can also check out the `examples <https://github.com/Lieturd/migrate-anything/tree/master/examples>`_.


Contributing
============

This project is run on GitHub using the issue tracking and pull requests here. If you want to contribute, feel free to `submit issues <https://github.com/Lieturd/migrate-anything/issues>`_ (incl. feature requests) or PRs here.
