#!/usr/bin/env python

import mltool

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

required = ['numpy>=1.6.1']
packages = ['mltool']

setup(
    name='mltool',
    version=mltool.__version__,
    description='Machine learning tool for regression.',
    long_description=open('README').read(),
    author='Maurizio Sambati',
    author_email='maurizio@skicelab.com',
    url='https://bitbucket.org/duilio/mltool',
    packages=packages,
    package_data={'': ['LICENSE']},
    scripts=['scripts/mltool'],
    include_package_data=True,
    install_requires=required,
    license=open('LICENSE').read(),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        ),
    )
