# -*- coding: utf-8 -*-
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pyvalidate import __version__ as package_version


setup(
    name="pyvalidate",
    version=package_version,
    author="Vahid Mardani",
    author_email="vahid.mardani@gmail.com",
    url="http://packages.python.org/pyvalidate",
    description="Python method's parameter validation library, as a pythonic decorator",
    maintainer="Vahid Mardani",
    maintainer_email="vahid.mardani@gmail.com",
    py_modules=['pyvalidate'],
    platforms=["any"],
    package_data={'':['README.TXT']},
    long_description=(lambda fname: open(os.path.join(os.path.dirname(__file__), fname)).read())('README.TXT'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: Freeware",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
        ],
    )
