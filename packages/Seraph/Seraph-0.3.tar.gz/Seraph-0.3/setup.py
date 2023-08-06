#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
setup(
        name='Seraph',
        version='0.3',
        description='A static blog generator, with jinja2 template and Markdown support.',
        author='wontoncc',
        author_email='wonton.cc@gmail.com',
        url='https://github.com/wontoncc/Seraph',
        packages=['Seraph','Seraph.extensions'],
        install_requires=['jinja2','markdown','PyYAML'],
        scripts=['scripts/Seraph.bat','scripts/Seraph','scripts/seraph-script.py'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Programming Language :: Python :: 3.2',
            'Topic :: Internet',
            'Topic :: Software Development :: Code Generators'
            ])
