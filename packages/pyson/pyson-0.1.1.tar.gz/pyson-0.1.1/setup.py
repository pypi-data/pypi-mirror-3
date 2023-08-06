#-*- coding: utf8 -*-
from distutils.core import setup
import os

SRC_DIR = 'src'

setup(name='pyson',
      version='0.1.1',
      description='Maniplates JSON-like structures consisting of dictionaries and lists.',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/py-pyson',
      long_description=('pyson is a Python library for manipulating JSON-like'
                        ' data structures. It has support for schemas and'
                        ' validation, searching and querying, differences,'
                        ' iteration over JSON-like structures, and more'),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          ],
      package_dir={ '': 'src' },
      packages=['pyson', 'pyson.iface', 'pyson.types', 'pyson.schemas',
                'pyson.util'],
      requires=['simplejson'],
)
