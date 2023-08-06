#-*- coding: utf8 -*-
from distutils.core import setup
import os

setup(name='binpack',
      version='0.3',
      description='Binary packing of data.',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/py-binpack',
      long_description=(
'''Binary packing of data. Easily creates file formats that hold arbitrary 
binary data that can be accessed with a dictionary-like interface.

Main features:
  * Transparent serialization of Python objects.
  * Transparent compression of data.
  * User can create arbitrary serialization/de-serialization functions.
  * Data can be saved or retrieved from any object that supports the file 
    protocol.
'''),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          ],
      package_dir={'': 'src'},
      py_modules=['binpack'],
      requires=[],
)
