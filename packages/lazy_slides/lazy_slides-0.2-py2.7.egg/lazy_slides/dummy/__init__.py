'''A dummy implementation of a search method.

Good for offline testing, etc.
'''

import os


def search(tag):
    if tag == 'fail':
        return None

    path = os.path.abspath(__file__)
    dirname = os.path.split(path)[0]
    return 'file://{}'.format(
        os.path.join(dirname, 'test_pattern.gif'))
