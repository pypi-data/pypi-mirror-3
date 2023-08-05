#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

install_requires = open("requirements.txt").read().split('\n')
readme_content = open("README.rst").read()

setup(
    name='ino',
    version='0.1.3',
    description='Command line toolkit for working with Arduino hardware',
    long_description=readme_content,
    author='Victor Nakoryakov, Amperka Team',
    author_email='victor@amperka.ru',
    license='MIT',
    keywords="arduino build system",
    url='http://inotool.org',
    packages=['ino', 'ino.commands'],
    scripts=['bin/ino'],
    data_files=[('', 'requirements.txt README.rst'.split)],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Embedded Systems",
    ],
)
