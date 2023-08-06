#!/usr/bin/env python
# vim: ft=python ts=4 sts=4 sw=4 et cc=80 fileencoding=utf-8


from setuptools import setup


setup(
    name="textutils",
    version="0.1",
    description="Small collection of string and text utilities",
    long_description=open('Readme.txt').read(),
    author="Aluísio Augusto Silva Gonçalves",
    author_email="kalug@kalug.net",
    url="https://bitbucket.org/AluisioASG/textutils.py",
    download_url="https://bitbucket.org/AluisioASG/textutils.py/downloads",
    license="Public Domain (CC0)",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: Public Domain",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    py_modules=['textutils'],
)
