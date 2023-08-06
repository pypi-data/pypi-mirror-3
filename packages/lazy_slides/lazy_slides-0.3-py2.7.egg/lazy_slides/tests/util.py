import contextlib
import os

def remove(path):
    try:
        os.remove(path)
    except OSError:
        pass

@contextlib.contextmanager
def temp_file(filename):
    with open(filename, 'w') as f:
        f.write('asdfasdf')

    yield

    remove(filename)
