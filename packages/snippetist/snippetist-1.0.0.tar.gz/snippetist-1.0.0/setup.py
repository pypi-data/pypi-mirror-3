#!/usr/bin/env python
from distutils.core import setup

setup(name='snippetist',
      version='1.0.0',
      description='Cross-editor snippet compiler',
#      long_description="""""",
      license='Apache License 2.0',
      author='myfreeweb',
      author_email='floatboth@me.com',
      url='https://github.com/myfreeweb/snippetist',
      requires=['PyYAML', 'pystache'],
      packages=['snippetist'],
      package_data={'snippetist': ['*.mustache']},
      scripts=['scripts/snippetist'],
      keywords=['text', 'snippet', 'textmate', 'sublime text 2', 'emacs', 'vim'],
      classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
      ],
)
