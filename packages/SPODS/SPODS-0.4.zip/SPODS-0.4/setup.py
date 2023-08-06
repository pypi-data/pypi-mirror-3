#!/usr/bin/env python

from distutils.core import setup

setup(
    name='SPODS',
    version='0.4',
    author='Sasha Bermeister',
    author_email='sbermeister@gmail.com',
    packages=['spods', 'spods.test'],
    scripts=[],
    url='https://github.com/sbermeister/SPODS/',
    license='LICENSE.txt',
    description='A lightweight database object serialiser for Python.',
    long_description=open('README.md').read(),
    install_requires=[],
)
