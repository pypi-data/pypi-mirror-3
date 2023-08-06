from setuptools import find_packages
from setuptools import setup
import os

VERSION = '0.3.2'

setup(
    description='Test',
    include_package_data=True,
    long_description=(
        open('README.rst').read() + '\n' +
        open('HISTORY.txt').read()
        ),
    name='experimental.pythonpackages',
    packages=find_packages(),
    version=VERSION,
)
