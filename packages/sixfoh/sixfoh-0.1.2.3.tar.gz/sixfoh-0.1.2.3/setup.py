#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="sixfoh",
    version="0.1.2.3",
    author="Tyler Ball",
    author_email="tyler@tylerball.net",
    description=(
        "Generates base sixfoh-encoded images for yer websites."),
    license="BSD",
    keywords="base64 encoding images css less",
    url="https://github.com/tylerball/sixfoh",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sixfoh = sixfoh.cli:main',
        ],
    },
    include_package_data=True,
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
)
