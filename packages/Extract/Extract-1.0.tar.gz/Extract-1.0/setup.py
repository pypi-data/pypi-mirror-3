# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import os
import sys
from distutils import log

long_desc = '''Extraction tool for model and observed data comparison'''

requires = ['coards', 'numpy', 'pydap']

setup(
    name='Extract',
    version='1.0',
    url='https://bitbucket.org/luizirber/extract',
    download_url='https://bitbucket.org/luizirber/extract/downloads',
    license='PSF',
    author='Luiz Irber',
    author_email='luiz.irber@gmail.com',
    description='Extraction tool for model and observed data intercomparison',
    long_description=long_desc,
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
