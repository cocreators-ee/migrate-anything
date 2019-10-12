.. image:: https://travis-ci.org/lieturd/migrate-anything.svg?branch=master
    :target: https://travis-ci.org/lieturd/migrate-anything
    :align: right

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :align: right

.. image:: https://codecov.io/gh/Lieturd/migrate-anything/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Lieturd/migrate-anything
    :align: right

Migrate anything - database (etc.) migration utility, especially for Python projects.


What is this?
=============

It's kinda annoying how often you run into the question of how to handle migrations in your project, and there hasn't seem to emerged any good, DB -agnostic, framework-agnostic, and storage-agnostic tool to manage them.

This project is an attempt to change that.


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

This would configure your migrations' status to be stored in a local file called ``migration_status.csv`` and set up your first migration script. If you have a ``my_db`` module that works like this you could just run this with the command

.. code-block:: shell

    migrate-anything migrations

Now in the real world you might want something more durable and a realistic example, so here's another (still hypothetical) version:

.. code-block:: python

    # __init__.py
    from migrate_anything import configure, KubernetesConfigMap

    configure(storage=KubernetesConfigMap("migrate-anything-status"))

.. code-block:: python

    # 01-initialize-db.py
    from pymongo import MongoClient

    client = MongoClient()  # Hope you're really not using defaults
    db = client.testdb

    def up():
        db.posts.insert_one({
            "id": "post-1",
            "title": "We're live!",
            "content": "This is our first post, yay."
        })
        db.posts.create_index("id")

    def down():
        db.posts.drop()

This would configure storage to a Kubernetes ConfigMap (if that class existed), and run migrations to MongoDB. There's also going to be storage modules to MongoDB available but this is way cooler.

Oh and your Kubernetes pods will likely require the necessary RBAC rules to manage their ConfigMap. It's unfortunately kinda complex, but I'm sure you can figure it out e.g. with this `guide <https://docs.bitnami.com/kubernetes/how-to/configure-rbac-in-your-kubernetes-cluster/>`_. Alternatively you can just use the MongoDB storage, or write your own - it's easy.

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

You can also check out the `examples <https://github.com/lieturd/migrate-anything/examples>`_.
