#!/usr/bin/env python

from setuptools import setup
import ngblog

setup(
    name='ngblog',
    version='0.1.1',
    license='BSD',
    description='A simple and easy to use plain-text-like blogging-engine.',
    long_description=open('README').read(),
    author='Nerd Gordo',
    author_email='nerdgordo@nerdgordo.com',
    url='http://nerdgordo.com/git/?p=ngblog.git',
    py_modules=['ngblog'],
    install_requires=['argparse', 'Werkzeug'],
    entry_points={'console_scripts': ['ngblog = ngblog:main']},
)
