import sys
from setuptools import setup

extra = {}

required = ['httplib2']

if sys.version_info[:2] < (2,6):
    required.append('simplejson')

setup(
    name = 'Embedly',
    version = '0.4',
    author = 'Embed.ly, Inc.',
    author_email = 'support@embed.ly',
    description = 'Python Library for Embedly',
    long_description=open('README.rst').read(),
    license = """
    Copyright (c) 2011, Embed.ly, Inc.
    All rights reserved.  Released under the 3-clause BSD license.
    """,
    url = "https://github.com/embedly/embedly-python",
    packages = ['embedly'],
    install_requires = required,
    zip_safe = True,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    **extra
)