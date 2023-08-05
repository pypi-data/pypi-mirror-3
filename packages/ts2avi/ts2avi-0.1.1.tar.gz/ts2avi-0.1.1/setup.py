#from distutils.core import setup
import os
from setuptools import setup

setup(
    name='ts2avi',
    version='0.1.1',
    description='A TS to AVI converter based on mplayer',
    author='Stephane Bugat',
    author_email='stephane.bugat@free.fr',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Topic :: Multimedia :: Video :: Conversion',
    ],
    url='http://pypi.python.org/pypi',
    scripts=['ts2avi.py'],
    long_description=r"""A TS to AVI converter written in Python.

TS files are generally produced by TV records from boxes like the freebox
provided by free.

This script extensively uses mencoder, which is generally provided by an
mplayer installation! See http://www.mplayerhq.hu for more information.
As it uses the subpress module, this script is supposed to work with
python >= 2.6. Please check your local version by a simple ``python -V``."""
)
