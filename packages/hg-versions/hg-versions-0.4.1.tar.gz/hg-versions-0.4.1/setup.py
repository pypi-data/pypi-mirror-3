# *-* encoding: utf-8 *-*
from setuptools import setup
import os

import versions

def read(*path):
    basepath = os.path.abspath(os.path.dirname(__file__))
    return open(os.path.join(basepath, *path)).read()

setup(name='hg-versions',
    version=versions.__version__,
    url='https://bitbucket.org/keimlink/hg-versions/src',
    author='Markus Zapke-Gruendemann',
    author_email='markus@keimlink.de',
    description=versions.__doc__,
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    license='GNU GPLv2+',
    py_modules=['versions'],
    classifiers=['Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control'
    ]
)
