import os
from setuptools import setup, find_packages


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="sixfoh",
    version="0.1.2",
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
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
)
