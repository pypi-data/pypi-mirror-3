#!/usr/bin/env python
from setuptools import setup
import simple_daemon

setup(
    name='simple_daemon',
    version=simple_daemon.__version__,
    description='Simple nix daemon',
    long_description=open('README.rst').read(),
    author='Imbolc',
    author_email='imbolc@imbolc.name',
    url='https://bitbucket.org/imbolc/simple_daemon',
    packages= ['simple_daemon'],
    install_requires=['single_access==0.0.2'],
    license='ISC',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ),
)
