#!/usr/bin/env python
import re, sys
from setuptools import setup, find_packages

# dep sugar.
_ver = sys.version_info

if _ver[0] == 2:
    dep = ['simplejson', 'requests>=0.13.1']
elif _ver[0] == 3:
    dep = ['requests>=0.13.1']

msinit = open('roxee/__init__.py').read()
author = re.search("__author__ = '([^']+)'", msinit).group(1)
version = re.search("__version__ = '([^']+)'", msinit).group(1)

setup(
    name='roxee',
    version=version,
    description='Roxee API v1.0',
    long_description=open('README').read(),
    author=author,
    author_email="manu@webitup.fr",
    url='https://github.com/webitup/python-roxee',
    packages=find_packages(),
    download_url='http://pypi.python.org/pypi/roxee/',
    keywords='roxee',
    package_data={'': ['LICENSE', 'README']},
    include_package_data=True,
    zip_safe=True,
    install_requires=dep,
    py_modules=['roxee'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2'
    ]
)