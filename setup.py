# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='dask_sparse_mtx',
    version='1.0.0',
    description='Toy dask sparse matrix multiplier',
    long_description=readme,
    author='Jonathan Dursi',
    author_email='jonathan@dursi.ca',
    url='https://github.com/ljdursi/dask-sparse-mtx',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
