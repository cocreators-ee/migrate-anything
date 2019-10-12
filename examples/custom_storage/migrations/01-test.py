from os import remove
from time import time

file = "test-file.txt"


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
