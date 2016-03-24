#!/usr/bin/env python

from urler import __version__
from setuptools import setup, find_packages

setup(
    name='urler',
    version=__version__,
    description='A class for URL-building/parsing/manipulation',
    long_description='',
    url='https://github.com/gtors/urler',
    py_modules=['urler'],
    license='MIT',
    platforms=['any'],
    author='Andrey Torsunov',
    author_email='andrey.torsunov@gmail.com',
    classifiers=[
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    install_requires=[
        'publicsuffixlist'
    ]
)
