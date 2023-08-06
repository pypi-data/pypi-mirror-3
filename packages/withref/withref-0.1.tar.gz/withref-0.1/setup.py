#!/usr/bin/env python

from setuptools import setup

with open('README.txt', 'r') as readme:
    README_TEXT = readme.read()
    readme.close()

setup(
    name='withref',
    version='0.1',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description="Use Python's with statement to simplify multi-level object dereferences, reminisent of Pascal's with statement",
    long_description=README_TEXT,
    url='https://bitbucket.org/jeunice/withref',
    py_modules=['withref'],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ]
)
