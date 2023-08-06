#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="readability-lxml",
    version="0.2.5",
    author="Yuri Baburov",
    author_email="burchik@gmail.com",
    description="fast python port of arc90's readability tool",
    test_suite = "tests.test_article_only",
    long_description=open("README").read(),
    license="Apache License 2.0",
    url="http://github.com/buriy/python-readability",
    #package_dir={'': 'readability'},
    #packages=find_packages('readability', exclude=["*.tests", "*.tests.*"]),
    packages=find_packages(),
    install_requires=[
        "chardet",
        "lxml"
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
)
