# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='ranger',
    version='0.1',
    description='',
    author='',
    author_email='',
    install_requires=[
        "pecan",
    ],
    test_suite='ranger',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['pbr'],
    pbr=True)
