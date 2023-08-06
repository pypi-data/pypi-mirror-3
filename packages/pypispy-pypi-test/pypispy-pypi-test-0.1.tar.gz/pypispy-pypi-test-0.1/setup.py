import os
from setuptools import setup, find_packages
import pypispy_pypi_test


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="pypispy-pypi-test",
    version=pypispy_pypi_test.__version__,
    description=read('README.md'),
    keywords='python packages maintenance',
    packages=find_packages(),
    author='Martin Brochhaus',
    author_email='martin.brochhaus@bitmazk.com',
    url="https://github.com/bitmazk/pypispy-pypi-test",
    include_package_data=True,
)
