# empty package for distributing data properly with setuptools
import os

VERSION = (1, 0, 3)

def pkg_path(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
