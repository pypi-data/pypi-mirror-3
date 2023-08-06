#! /usr/bin/env python

from setuptools import setup

readme = open('README.txt', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='namedentities',
    version='1.0.4',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Simple way to convert numeric HTML entities to far more readable named entities.',
    long_description=README_TEXT,
    url='http://bitbucket.org/jeunice/namedentities',
    py_modules=[],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
