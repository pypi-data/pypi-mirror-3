#-*- coding: utf8 -*-
from distutils.core import setup
import os

setup(name='simpleinput',
      version='0.1',
      description='Request inpunts of specific types.',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/py-simpleinput',
      long_description=(
'''Request inputs of specific types from user. Useful for building simple CLI
applications. 

simpleinput has support to:
 * Boolean inputs
 * Numeric inputs
 * Choices
 
Each input function has a unified interface and can be called from within a user
specified context that defines many common aspects of execution. 
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
      py_modules=['simpleinput'],
      requires=[],
)
