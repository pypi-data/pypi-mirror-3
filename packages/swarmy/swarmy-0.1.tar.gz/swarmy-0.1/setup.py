
try:
    from setuptools import setup
except ImportError:
    print "Falling back to distutils. Functionality may be limited."
    from distutils.core import setup

config = {
    'description'  : 'A collection of utils',
    'author'       : 'Brandon Sandrowicz',
    'url'          : 'http://github.com/bsandrow/swarmy',
    'author_email' : 'brandon@sandrowicz.org',
    'version'      : 0.1,
    'packages'     : ['swarmy'],
    'name'         : 'swarmy',
    'test_suite'   : 'tests',
}

setup(**config)
