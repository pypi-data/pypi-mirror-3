#! /usr/bin/env python
try:
    from setuptools import setup
except ImportError, err:
    from distutils.core import setup

def get_version():
    for line in open( 'globalsub.py' ):
        if line.startswith( '__version__' ):
            return line.split( '=' )[1].strip().strip('"').strip("'")
    raise RuntimeError( 'Unable to determine version from globalsub.py' )

if __name__ == "__main__":
    setup(
        name='globalsub',
        author='Mike Fletcher, Gustavo Niemeyer',
        author_email='mcfletch@vrplumber.com',
        description='Global substitution functions for Python unit tests',
        zip_safe=False,
        py_modules = ['globalsub'],
        version = get_version(),
        url = 'http://pypi.python.org/pypi/globalsub/',
        license = 'BSD',
    )
