#!/usr/bin/env python
from setuptools import setup
import single_access

setup(
    name='single_access',
    version=single_access.__version__,
    description='Single access to run python script',
    long_description=open('README.rst').read(),
    author='Imbolc',
    author_email='imbolc@imbolc.name',
    url='https://bitbucket.org/imbolc/single_access',
    packages= ['single_access'],
    install_requires=[],
    license='ISC',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ),
)
