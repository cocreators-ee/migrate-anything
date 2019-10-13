from functools import wraps
import os

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


def remove_files(files):
    """
    Delete a bunch of files if they exist
    :param List[str] files:
    """
    for file in files:
        try:
            os.remove(file)
            print ("Removed {}".format(file))
        except OSError:
            pass


def clean_files(files):
    """
    Remove test artifacts before and after running the test
    :param List[str] files:
    """

    def _decorator(f):
        @wraps(f)
        def _wraps(*args, **kwargs):
            remove_files(files)
            try:
                f(*args, **kwargs)
            finally:
                remove_files(files)

        return _wraps

    return _decorator
