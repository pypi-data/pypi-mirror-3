#!/usr/bin/env python
# -*- coding: utf-8 -*-

long_desc="""Mainly inspired by hyde, it is now a very alpha version.

=====
Usage
=====
Initate the site:
    Seraph --init [DIR]
Build the site:
    cd [DIR]
    Seraph --build
Check your site in "build/".

=====
Get Code in Developement
=====
Please refer to the `code on github<https://github.com/wontoncc/Seraph>`_."""

from distutils.core import setup
setup(
        name='Seraph',
        version='0.33',
        description='A static blog generator, with jinja2 template and Markdown support.',
        author='wontoncc',
        author_email='wonton.cc@gmail.com',
        url='https://github.com/wontoncc/Seraph',
        packages=['Seraph','Seraph.extensions'],
        install_requires=['jinja2','markdown','PyYAML'],
        scripts=['scripts/Seraph.bat','scripts/Seraph','scripts/seraph-script.py'],
        long_description=long_desc,
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Programming Language :: Python :: 3.2',
            'Topic :: Internet',
            'Topic :: Software Development :: Code Generators'
            ])