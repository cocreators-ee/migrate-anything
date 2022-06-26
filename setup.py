# -*- coding: utf-8 -*-
from setuptools import setup
from io import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="migrate-anything",
    entry_points={"console_scripts": ["migrate-anything = migrate_anything.main:main"]},
    version="0.1.7",
    description="Helps manage migrations for databases and anything else",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/cocreators-ee/migrate-anything",
    author="Cocreators OÜ",
    author_email="janne@cocreators.ee",
    packages=["migrate_anything", "migrate_anything.storage"],
    keywords="migrate database db release",
    python_requires=">=3.6, <4",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    project_urls={
        "Bug Reports": "https://github.com/cocreators-ee/migrate-anything/issues",
        "Source": "https://github.com/cocreators-ee/migrate-anything/",
    },
)
