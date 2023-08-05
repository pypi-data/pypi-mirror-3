#!/usr/bin/env python
from setuptools import setup
import goto

setup(
    name='goto',
    version=goto.__version__,
    description='Urllib object wrapper',
    long_description=open('README.rst').read(),
    author='Imbolc',
    author_email='imbolc@imbolc.name',
    url='https://bitbucket.org/imbolc/goto',
    packages= ['goto', ],
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
