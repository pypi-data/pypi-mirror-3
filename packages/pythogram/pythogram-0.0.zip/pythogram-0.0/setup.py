from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(
    name = "pythogram",
    version = version,
    description = "A django app for distributed photogrammetric computations",
    long_description="""\
    """,
    classifiers = [], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords = '',
    author = 'Christodoulos Psaltis',
    author_email = 'cpsaltis@unweb.me',
    url = 'http://github.com/cpsaltis/pythogram',
    license = 'BSD License',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    zip_safe = False,
    install_requires = [
        # -*- Extra requirements: -*-
    ],
    entry_points = """
    # -*- Entry points: -*-
    """,
)
