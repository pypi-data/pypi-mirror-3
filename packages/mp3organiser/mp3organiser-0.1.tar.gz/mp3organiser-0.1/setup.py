#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="mp3organiser",
    version="0.1",
    packages=find_packages(),
    scripts=['bin/mp3organiser'],

    install_requires=['mutagen>=1.20'],

    author="Brendan Maguire",
    author_email="maguire.brendan@gmail.com",
    description="Organises and tags mp3 files and folders",
    long_description=open('README').read(),
    license="MIT",
    keywords="mp3 tag organise",
)
