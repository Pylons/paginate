#!/usr/bin/env python

from distutils.core import setup

setup(name='paginate',
      version='0.4.0',
      description='Divides large result sets into pages',
      author='Christoph Haas',
      author_email='email@christoph-haas.de',
      url='http://workaround.org/paginate/',
      packages=['paginate'],
      long_description="""
This module helps divide up large result sets into pages or chunks.
The user gets displayed one page at a time and can navigate to other pages.
It is especially useful when developing web interfaces and showing the
users only a selection of information at a time.
""",
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules",
               ],
     )

