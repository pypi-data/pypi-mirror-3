#!/usr/bin/env python
from distutils.core import setup
setup(
    name='untinyurl',
    py_modules=['untinyurl'],
    version='0.1',
    description='Un-shorten urls found in given text',
    author='Julien Palard',
    author_email='julien@palard.fr',
    url='https://github.com/JulienPalard/untinyurl',
    download_url='https://github.com/JulienPalard/Pipe/tarball/master',
    long_description=open('README').read(),
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Console",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        ]
)
