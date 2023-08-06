import os
import unittest

def run():
    l = unittest.TestLoader()
    s = l.discover(os.path.dirname(__file__))
    unittest.TextTestRunner().run(s)

if __name__ == '__main__':
    run()
