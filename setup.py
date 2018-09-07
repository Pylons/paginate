import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGELOG.txt')) as f:
    CHANGES = f.read()

setup(
    name='paginate',
    version='0.5.6',
    description="Divides large result sets into pages for easier browsing",
    long_description=README + '\n\n' + CHANGES,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Pyramid',
        'Framework :: Flask',
        'Framework :: Pylons',
        'Framework :: Django',
    ],
    keywords='pagination paginate pages',
    author='Christoph Haas',
    author_email='email@christoph-haas.de',
    url='https://github.com/Signum/paginate',
    license='MIT',
    packages=find_packages(),
    extras_require={
        "dev": ["pytest", "tox"],
        "lint": ["black"],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points=""" """,
)
