#! /usr/bin/env python

from setuptools import setup, find_packages

readme = open('README.txt', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='namedentities',
    version='1.0.8',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Simple way to convert numeric HTML entities to far more readable named entities.',
    long_description=README_TEXT,
    url='http://bitbucket.org/jeunice/namedentities',
    packages = find_packages(),
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
