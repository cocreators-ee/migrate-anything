import fnmatch
import os
from functools import wraps
from shutil import rmtree

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


def find_cache_files():
    """
    Finds cache files, __pycache__ and *.pyc
    :return List[str]:
    """
    files = []

    for root, dirnames, filenames in os.walk("src"):
        for filename in fnmatch.filter(filenames, "*.pyc"):
            files.append(os.path.join(root, filename))

    for root, dirnames, filenames in os.walk("src"):
        for filename in fnmatch.filter(filenames, "__pycache__"):
            files.append(os.path.join(root, filename))

    return files


def remove_files(files):
    """
    Delete a bunch of files if they exist
    :param List[str] files:
    """
    for file in files:
        try:
            rmtree(file)
            print ("Removed {}".format(file))
        except OSError:
            pass


def clean_filesystem(files=[]):
    """
    Remove given files + python cache files
    :param List[str] files:
    """
    remove_files(files + find_cache_files())


def clean_files(files):
    """
    Remove test artifacts before and after running the test
    :param List[str] files:
    """

    def _decorator(f):
        @wraps(f)
        def _wraps(*args, **kwargs):
            clean_filesystem(files)
            try:
                f(*args, **kwargs)
            finally:
                clean_filesystem(files)

        return _wraps

    return _decorator
