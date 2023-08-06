#!/usr/bin/env python

import mp3organiser

from setuptools import setup, find_packages


setup(
    name="mp3organiser",
    version=mp3organiser.VERSION,
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'mp3org = mp3organiser:main',
        ],
    },
    scripts=['bin/mp3organiser'],

    install_requires=['mutagen>=1.20'],

    author="Brendan Maguire",
    author_email="maguire.brendan@gmail.com",
    description="Organises and tags mp3 files and folders",
    long_description=open('README').read(),
    license="MIT",
    keywords="mp3 tag organise",
)
