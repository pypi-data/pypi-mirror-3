#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PyTTY works with Python 2.7 and above only
import sys
if sys.version_info[0:2] < (2, 7) :
    raise RuntimeError('Python 2.7 or above is required for this package.')


from src import __author__, __credits__, __doc__, __version__
from distutils.core import setup


if __name__ == '__main__' : setup(
    #
    ###########################################################################
    #
    # PyPI settings (for pypi.python.org)
    #
    name             = 'PyTTY',                   # Name of project, not module
    version          = __version__.split()[0],
    description      = __doc__.splitlines()[0],
    long_description = '\n'.join(__doc__.splitlines()[2:]),
    maintainer       = 'Arc Riley',
    maintainer_email = 'arcriley@gmail.org',
    url              = 'http://www.pytty.org/',
    download_url     = 'http://pypi.python.org/pypi/PyTTY',
    license          = 'GNU Lesser General Public License version 3 (LGPLv3)',
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Communications',
        'Topic :: Terminals :: Serial',
    ],
    #
    ###########################################################################
    #
    # Package settings
    #
    packages         = ['pytty'],
    package_dir      = {'pytty' : 'src'},
    #
    ###########################################################################
)
