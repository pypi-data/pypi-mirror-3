from distribute_setup import use_setuptools
use_setuptools()

import sys
from setuptools import setup

setup(
    name='vic-txZMQ',
    version='0.5.1',
    packages=['txzmq','txzmq.test'],
    license='GPLv2',
    author='Victor Lin, Andrey Smirnov',
    author_email='bornstub@gmail.com',
    url='http://pypi.python.org/pypi/vic-txZMQ',
    description='Twisted bindings for ZeroMQ',
    long_description=open('README.rst').read(),
    install_requires=[
        "Twisted>=10.0", 
        "pyzmq-ctypes>=2.1" if sys.subversion[0] == "PyPy" else "pyzmq>=2.1" 
    ],
    tests_require=[
        'nose-cov'
    ],
    setup_requires=[
        'nose>=1.0'
    ],
)
