import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    

setup(
    name            = "pile",
    version         = "0.1",
    description     = "A little client side package management",
    author          = "Wess Cope",
    author_email    = "wess@wattz.net",
    url             = "http://wess.github.com/pile",
    packages        = ['pile', 'pile.packages',],
    license         = 'MIT',
    classifiers     = (
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    )
)