#! /usr/bin/env python
try:
    from setuptools import setup
except ImportError, err:
    from distutils.core import setup

def get_version():
    for line in open( 'fakelion.py' ):
        if line.startswith( '__version__' ):
            return line.split( '=' )[1].strip().strip('"').strip("'")
    raise RuntimeError( 'Unable to determine version from fakelion.py' )

if __name__ == "__main__":
    setup(
        name='fakelion',
        author='Mike C. Fletcher',
        author_email='mcfletch@vrplumber.com',
        description='Script to produce fake translations for .po files',
        zip_safe=False,
        py_modules = [
            'fakelion',
        ],
        requires = [
            'polib',
        ],
        version = get_version(),
        url = 'https://launchpad.net/fakelion',
        license = 'BSD',
    )
