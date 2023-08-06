from setuptools import find_packages
from setuptools import setup

VERSION = '0.0.6'

setup(
    include_package_data=True,
    name='experimental.pythonpackages',
    packages=find_packages(),
    version=VERSION,
)
