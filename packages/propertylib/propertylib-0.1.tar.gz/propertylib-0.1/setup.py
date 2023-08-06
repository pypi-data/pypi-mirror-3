#-*- coding: utf8 -*-
from distutils.core import setup
import os

setup(name='propertylib',
      version='0.1',
      description='Simple library that implements a few special purpose properties.',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/py-propertylib',
      long_description=(
'''Implements a few convenient special purpose properties. Some of its features:

* Cached values for attribute values computed from expensive computations
* Emulate attributes with default values
* Support for defining getter/setter/deleter functions using a convenient class notation.
'''),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          ],
      package_dir={ '': 'src' },
      packages=['propertylib'],
      requires=[],
)
