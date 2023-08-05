#!/usr/bin/env python

import os.path
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pypq',
      version='0.1.1',
      description='Python PostgreSQL DBAPI 2.0 compliant driver using ctypes and libpq.so, works with PyPy',
      long_description=read('README'),
      author='Igor Katson',
      author_email='igor.katson@gmail.com',
      url='https://bitbucket.org/descent/pypq',
      packages=['pypq', 'pypq.django_backend'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Database',
          'Topic :: Database :: Front-Ends',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
     )
