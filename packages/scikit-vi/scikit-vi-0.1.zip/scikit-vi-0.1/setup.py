#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

VERSION = '0.1'
LONG_DESCRIPTION = """
	scikit-vi (aka skvi) is a scikit which provides virtual instrument objects. 
The goal of this project is to provide a centralized repository for virtual 
instruments written in python.
"""
setup(name='scikit-vi',
	version=VERSION,
	license='gpl',
	description='Scikit providing Virtual Instruments',
	long_description=LONG_DESCRIPTION,
	author='Alex Arsenovic',
	author_email='arsenovic@virginia.edu',
	url='https://github.com/scikit-vi/scikit-vi',
	packages=find_packages(),
	requires = [
		'pyvisa',
		'numpy',
		],
	package_dir={'skvi':'skvi'},
	)

