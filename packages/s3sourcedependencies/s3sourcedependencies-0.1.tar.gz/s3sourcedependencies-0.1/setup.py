#!/usr/bin/env python
import os
from setuptools import setup


"""The path to the README file."""
README_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'README.rst')


setup(
    name='s3sourcedependencies',
    version='0.1',
    description=(
        'Download and install from private source distributions hosted on '
        'Amazon S3.'),
    long_description=open(README_PATH, 'r').read(),
    keywords='setuptools s3 dependencies s3sourceuploader',
    author='Ion Scerbatiuc',
    author_email='delinhabit@gmail.com',
    license='BSD',
    url='https://bitbucket.org/delinhabit/s3sourcedependencies',
    py_modules=['s3dependencies'],
    install_requires=["boto",],
    entry_points={
        "distutils.setup_keywords": [
            "s3dependencies = s3dependencies:load",
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
