#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup


setup(
    name='whoosh-igo',
    version='0.7',
    description='tokenizers for Whoosh designed for Japanese language',
    long_description = open('README').read() + "\n\n" + open('CHANGES').read(),
    author='Hideaki Takahashi',
    author_email='mymelo@gmail.com',
    url='https://github.com/hideaki-t/whoosh-igo/',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Natural Language :: Japanese',
                 'Operating System :: OS Independent',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.2',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Text Processing :: Linguistic',
                 ],
    keywords=['japanese', 'tokenizer',],
    license='Apache License, Version 2.0',
    packages=['whooshjp'],
    )
