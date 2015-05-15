from setuptools import setup, find_packages

import sys, os

setup(
    name='paginate',
    version='0.4.3',
    description="Divides large result sets into pages for easier browsing",
    long_description="""
        This module helps divide up large result sets into pages or chunks.
        The user gets displayed one page at a time and can navigate to other pages.
        It is especially useful when developing web interfaces and showing the
        users only a selection of information at a time.
        """,

    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    keywords='pagination paginate pages',
    author='Christoph Haas',
    author_email='email@christoph-haas.de',
    url='https://github.com/Signum/paginate',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points=""" """,
)
